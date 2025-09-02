import os
import json
from datetime import datetime
from typing import Tuple, Any, Dict, Optional

# Optional import for Gemini LLM; monitor works heuristically if not present
try:
    import google.generativeai as genai
except Exception:
    genai = None


class GeminiClientWrapper:
    def __init__(self, api_key: str):
        if genai is None:
            raise RuntimeError("google.generativeai not installed.")
        genai.configure(api_key=api_key)
        self.model_name = "gemini-1.5-flash"

    def generate_content(self, prompt: str) -> str:
        model = genai.GenerativeModel(self.model_name)
        resp = model.generate_content(prompt)
        return getattr(resp, "text", str(resp))


class AgentMonitor:
    def __init__(
        self,
        api_key: Optional[str] = None,
        threshold: float = 0.8,
        max_retries: int = 2,
        log_dir: str = "Agent_Monitor/logs",
    ):
        self.threshold = threshold
        self.max_retries = max_retries
        self.log_dir = log_dir
        os.makedirs(self.log_dir, exist_ok=True)
        self.logs = []
        self.client = None
        if api_key:
            if genai is None:
                raise RuntimeError(
                    "google.generativeai is not installed in this environment."
                )
            self.client = GeminiClientWrapper(api_key)

    def judge_code(self, code: Any) -> Tuple[float, str]:
        """
        Returns (score in 0..1, reason).
        Accepts any payload (strings, dicts) — converts to string safely.
        """
        if isinstance(code, str):
            code_str = code
        else:
            try:
                code_str = json.dumps(code, ensure_ascii=False)
            except Exception:
                code_str = str(code)

        if not self.client:
            score = 0.5
            reason = "Heuristic fallback: no LLM client configured."
            if "TODO" not in code_str and len(code_str) > 30:
                score = 0.75
                reason = "Heuristic: code present and non-trivial."
            lowered = code_str.lower()
            if "merge" in lowered or "sort" in lowered:
                score = min(0.95, score + 0.1)
                reason = reason + " Keyword match increased score."
            return float(score), reason

        prompt = (
            "You are a code quality judge. Rate the following code in a JSON object with fields:\n"
            "  score: float between 0.0 and 1.0 (higher is better)\n"
            "  reason: short explanation\n\n"
            f"CODE:\n{code_str}\n\nRespond ONLY with valid JSON."
        )
        try:
            raw = self.client.generate_content(prompt).strip()
            try:
                parsed = json.loads(raw)
                score = float(parsed.get("score", 0.0))
                reason = parsed.get("reason", raw)
                return max(0.0, min(1.0, score)), str(reason)
            except Exception:
                import re

                m = re.search(r"([01](?:\.\d+)?)", raw)
                if m:
                    score = float(m.group(1))
                    return max(0.0, min(1.0, score)), raw
                return 0.5, raw
        except Exception as e:
            return 0.0, f"LLM error: {e}"

    def enhance_code(self, code: str) -> str:
        """
        Enhance code using LLM if available; else heuristic add-on.
        """
        if not self.client:
            try:
                return code + "\n// Enhanced (heuristic): please implement details."
            except Exception:
                return str(code) + "\n// Enhanced (heuristic)."

        prompt = (
            "You are a code improver. Improve the following code for correctness, safety, and efficiency.\n"
            "Return only the improved code.\n\n"
            f"CODE:\n{code}\n"
        )
        try:
            improved = self.client.generate_content(prompt)
            return improved
        except Exception:
            return code

    def monitor_agent(
        self, agent_name: str, payload: Any, field_hint: Optional[str] = None
    ) -> Tuple[Any, Dict]:
        """
        Inspect payload, judge, enhance if needed, return updated payload and minimal log entry.
        """
        is_data_dict = isinstance(payload, dict)
        target_key = None
        value = None

        if is_data_dict:
            if field_hint and field_hint in payload:
                target_key = field_hint
                value = payload.get(target_key)
            else:
                for key in (
                    "code",
                    "reviewed_code",
                    "review",
                    "tests",
                    "analysis",
                    "execution_results",
                ):
                    if key in payload and payload.get(key) is not None:
                        target_key = key
                        value = payload.get(key)
                        break

            if value is None:
                try:
                    orig_text = json.dumps(payload, ensure_ascii=False)
                except Exception:
                    orig_text = str(payload)
                target_key = None
        else:
            value = payload

        # Skip judging execution_results structured data
        if target_key == "execution_results":
            log_entry = {
                "agent_name": agent_name,
                "initial_score": None,
                "initial_code": None,
                "final_score": None,
                "final_code": None,
            }
            self.logs.append(log_entry)
            return payload, log_entry

        if value is None:
            orig_text = ""
        elif isinstance(value, str):
            orig_text = value
        else:
            try:
                orig_text = json.dumps(value, ensure_ascii=False)
            except Exception:
                orig_text = str(value)

        score, reason = self.judge_code(orig_text)

        final_text = orig_text
        final_score = score

        retries = 0
        while final_score < self.threshold and retries < self.max_retries:
            improved = self.enhance_code(final_text)
            new_score, new_reason = self.judge_code(improved)
            final_text = improved
            final_score = new_score
            retries += 1

        log_entry = {
            "agent_name": agent_name,
            "initial_score": float(score),
            "initial_code": orig_text,
            "final_score": float(final_score),
            "final_code": final_text,
        }
        self.logs.append(log_entry)

        if is_data_dict and target_key:
            payload[target_key] = final_text
            return payload, log_entry

        if not is_data_dict:
            return final_text, log_entry

        return payload, log_entry

    def save_run_log(self, run_name: Optional[str] = None) -> str:
        """
        Save current self.logs to a JSON file. Returns the saved filepath.
        """
        timestamp = run_name or datetime.now().strftime("%Y%m%d_%H%M%S")
        filepath = os.path.join(self.log_dir, f"run_{timestamp}.json")
        with open(filepath, "w", encoding="utf-8") as f:
            json.dump(self.logs, f, indent=2, ensure_ascii=False)
        print(f"[AgentMonitor] Logs saved to {filepath}")
        # Clear logs for next run
        self.logs = []
        return filepath

