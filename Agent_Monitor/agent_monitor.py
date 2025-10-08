# Agent_Monitor/agent_monitor.py
import os
import json
import time
from datetime import datetime
from typing import Tuple, Any, Dict, Optional

try:
    import google.generativeai as genai
except Exception:
    genai = None


class GeminiClientWrapper:
    def __init__(self, api_key: str, model_name: str = "gemini-2.0-flash"):
        if genai is None:
            raise RuntimeError("google.generativeai not installed.")
        genai.configure(api_key=api_key)
        self.model_name = model_name

    def generate_content(self, prompt: str) -> str:
        model = genai.GenerativeModel(self.model_name)
        resp = model.generate_content(prompt)
        return getattr(resp, "text", str(resp))


class AgentMonitor:
    """
    Per-agent monitor: LLM scoring, enhancement loop, logs and summary writer.
    """

    def __init__(self, api_key: Optional[str] = None, threshold: float = 0.6, max_retries: int = 2, log_dir: str = "logs"):
        self.threshold = threshold
        self.max_retries = max_retries
        self.log_dir = log_dir
        os.makedirs(self.log_dir, exist_ok=True)
        self.logs = []
        self.client = GeminiClientWrapper(api_key) if api_key else None

    def _score_multi_llm(self, text: str) -> Dict[str, float]:
        def clamp(x):
            try:
                v = float(x)
                return max(0.0, min(1.0, v))
            except Exception:
                return 0.0
        
        def extract_json(raw_text: str) -> str:
            """Extract JSON from markdown code blocks if present"""
            raw_text = raw_text.strip()
            # Remove markdown code blocks
            if raw_text.startswith("```json"):
                raw_text = raw_text[7:]  # Remove ```json
            elif raw_text.startswith("```"):
                raw_text = raw_text[3:]  # Remove ```
            if raw_text.endswith("```"):
                raw_text = raw_text[:-3]  # Remove closing ```
            return raw_text.strip()

        personal_prompt = (
            "You are an evaluator. Return ONLY JSON {'personal_score': <0..1>} for the content below.\n\n"
            f"CONTENT:\n{text}"
        )
        personal_score = 0.0
        try:
            personal_raw = self.client.generate_content(personal_prompt).strip()
            personal_raw = extract_json(personal_raw)
            parsed = json.loads(personal_raw)
            personal_score = clamp(parsed.get("personal_score", 0.0))
        except Exception:
            personal_score = 0.0

        other_prompt = (
            "Return ONLY a JSON with fields in [0,1]: factual_accuracy, clarity, safety, code_correctness, complexity.\n\n"
            f"CONTENT:\n{text}"
        )
        parsed_other = {}
        try:
            other_raw = self.client.generate_content(other_prompt).strip()
            other_raw = extract_json(other_raw)
            parsed_other = json.loads(other_raw)
        except Exception:
            parsed_other = {}

        return {
            "personal_score": personal_score,
            "factual_accuracy": clamp(parsed_other.get("factual_accuracy", 0.0)),
            "clarity": clamp(parsed_other.get("clarity", 0.0)),
            "safety": clamp(parsed_other.get("safety", 0.0)),
            "code_correctness": clamp(parsed_other.get("code_correctness", 0.0)),
            "complexity": clamp(parsed_other.get("complexity", 0.0)),
        }

    def _score_multi_heuristic(self, text: str) -> Dict[str, float]:
        t = text.lower() if isinstance(text, str) else str(text).lower()
        nontrivial = 1.0 if len(t) > 60 else 0.4
        has_code_hint = any(k in t for k in ["def ", "class ", "{", "};", "public ", "//", "print("])
        sorted_hint = any(k in t for k in ["sort", "merge", "binary search", "dp", "graph", "tree"])

        personal = 0.6 * nontrivial + (0.2 if has_code_hint else 0.0) + (0.1 if sorted_hint else 0.0)
        factual = 0.5 + (0.2 if sorted_hint else 0.0)
        clarity = 0.5 + (0.2 if "\n" in t or "." in t else 0.0)
        safety = 0.7 - (0.2 if "eval(" in t or "exec(" in t else 0.0)
        correctness = 0.5 + (0.2 if has_code_hint else 0.0)
        complexity = 0.3 + (0.3 if sorted_hint else 0.0)

        def clamp(x): return max(0.0, min(1.0, x))
        return {
            "personal_score": clamp(personal),
            "factual_accuracy": clamp(factual),
            "clarity": clamp(clarity),
            "safety": clamp(safety),
            "code_correctness": clamp(correctness if has_code_hint else 0.2),
            "complexity": clamp(complexity),
        }

    def _score_multi(self, text: str) -> Dict[str, float]:
        if self.client:
            try:
                return self._score_multi_llm(text)
            except Exception:
                return self._score_multi_heuristic(text)
        return self._score_multi_heuristic(text)

    def _enhance(self, text: str) -> str:
        if not self.client:
            return f"{text}\n// Enhanced (heuristic): clarify naming, handle edge-cases, add comments."
        prompt = (
            "Improve the following content for correctness, clarity, safety, and efficiency. "
            "Return ONLY the improved content (no explanations).\n\n"
            f"CONTENT:\n{text}"
        )
        try:
            return self.client.generate_content(prompt)
        except Exception:
            return text

    def monitor_agent(self, agent_name: str, payload: Any, field_hint: Optional[str] = None) -> Tuple[Any, Dict]:
        t0 = time.time()
        is_data_dict = isinstance(payload, dict)
        target_key, value = None, None

        if is_data_dict:
            if field_hint and field_hint in payload:
                target_key = field_hint
                value = payload.get(target_key)
            else:
                for key in ("code", "review", "tests", "analysis", "answer", "execution_results"):
                    if key in payload and payload.get(key) is not None:
                        target_key = key
                        value = payload.get(key)
                        break
        else:
            value = payload

        # skip structured execution results
        if target_key == "execution_results":
            latency = time.time() - t0
            log_entry = {
                "agent_name": agent_name,
                "initial_code": None,
                "final_code": None,
                "initial_personal_score": None,
                "final_personal_score": None,
                "personal_score": None,
                "factual_accuracy": None,
                "clarity": None,
                "safety": None,
                "code_correctness": None,
                "complexity": None,
                "enhancement_loops": 0,
                "latency": latency,
                "token_usage": 0,
            }
            self.logs.append(log_entry)
            return payload, log_entry

        # stringify value
        if value is None:
            text = ""
        elif isinstance(value, str):
            text = value
        else:
            try:
                text = json.dumps(value, ensure_ascii=False)
            except Exception:
                text = str(value)

        # initial scoring
        initial_scores = self._score_multi(text)
        initial_personal = float(initial_scores.get("personal_score", 0.0))

        loops = 0
        final_text = text
        scores = initial_scores

        while scores["personal_score"] < self.threshold and loops < self.max_retries:
            improved = self._enhance(final_text)
            improved_scores = self._score_multi(improved)
            if improved_scores["personal_score"] >= scores["personal_score"]:
                final_text = improved
                scores = improved_scores
            loops += 1

        latency = time.time() - t0
        approx_tokens = max(1, len(final_text) // 4)
        final_personal = float(scores.get("personal_score", 0.0))

        log_entry = {
            "agent_name": agent_name,
            "initial_code": text,
            "final_code": final_text,
            "initial_personal_score": initial_personal,
            "final_personal_score": final_personal,
            "personal_score": final_personal,
            "factual_accuracy": float(scores.get("factual_accuracy", 0.0)),
            "clarity": float(scores.get("clarity", 0.0)),
            "safety": float(scores.get("safety", 0.0)),
            "code_correctness": float(scores.get("code_correctness", 0.0)),
            "complexity": float(scores.get("complexity", 0.0)),
            "enhancement_loops": loops,
            "latency": latency,
            "token_usage": approx_tokens,
        }
        self.logs.append(log_entry)

        if is_data_dict and target_key:
            payload[target_key] = final_text
            return payload, log_entry
        if not is_data_dict:
            return final_text, log_entry
        return payload, log_entry

    def save_run_log(self, run_name: Optional[str] = None) -> str:
        timestamp = run_name or datetime.now().strftime("%Y%m%d_%H%M%S")
        filepath = os.path.join(self.log_dir, f"run_{timestamp}.json")
        with open(filepath, "w", encoding="utf-8") as f:
            json.dump(self.logs, f, indent=2, ensure_ascii=False)
        print(f"[AgentMonitor] Logs saved to {filepath}")
        # don't clear logs here (save_json_summary expects logs)
        return filepath

    def save_json_summary(self, filepath: Optional[str] = None, collective_score: Optional[float] = None) -> str:
        summary = {"agents": {}, "collective_score": (collective_score if collective_score is not None else None)}
        for log in self.logs:
            name = log.get("agent_name")
            if not name:
                continue
            init = log.get("initial_personal_score")
            final = log.get("final_personal_score")
            if init is None:
                init = log.get("personal_score")
            if final is None:
                final = log.get("personal_score")
            summary["agents"][name] = {"initial": init, "final": final}
        timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
        if filepath is None:
            filepath = os.path.join(self.log_dir, f"summary_{timestamp}.json")
        os.makedirs(os.path.dirname(filepath), exist_ok=True)
        with open(filepath, "w", encoding="utf-8") as f:
            json.dump(summary, f, indent=2, ensure_ascii=False)
        print(f"[AgentMonitor] Summary saved to {filepath}")
        return filepath
