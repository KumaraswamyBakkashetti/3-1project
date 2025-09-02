# # Agent_Monitor/agent_monitor.py
# import os
# import json
# from datetime import datetime
# from typing import Tuple, Any, Dict, Optional

# # Optional import for Gemini LLM; monitor works heuristically if not present
# try:
#     import google.generativeai as genai
# except Exception:
#     genai = None


# class GeminiClientWrapper:
#     def __init__(self, api_key: str):
#         if genai is None:
#             raise RuntimeError("google.generativeai not installed.")
#         genai.configure(api_key=api_key)
#         self.model_name = "gemini-1.5-flash"

#     def generate_content(self, prompt: str) -> str:
#         model = genai.GenerativeModel(self.model_name)
#         resp = model.generate_content(prompt)
#         return getattr(resp, "text", str(resp))


# class AgentMonitor:
#     def __init__(self,
#                  api_key: Optional[str] = None,
#                  threshold: float = 0.8,
#                  max_retries: int = 2,
#                  log_dir: str = "Agent_Monitor/logs"):
#         self.threshold = threshold
#         self.max_retries = max_retries
#         self.log_dir = log_dir
#         os.makedirs(self.log_dir, exist_ok=True)
#         self.logs = []
#         self.client = None
#         if api_key:
#             if genai is None:
#                 raise RuntimeError("google.generativeai is not installed in this environment.")
#             self.client = GeminiClientWrapper(api_key)

#     def judge_code(self, code: Any) -> Tuple[float, str]:
#         """
#         Returns (score in 0..1, reason).
#         Accepts any payload (strings, dicts) — converts to string safely.
#         """
#         # normalize to string
#         if isinstance(code, str):
#             code_str = code
#         else:
#             try:
#                 code_str = json.dumps(code, ensure_ascii=False)
#             except Exception:
#                 code_str = str(code)

#         # Heuristic fallback if no client
#         if not self.client:
#             score = 0.5
#             reason = "Heuristic fallback: no LLM client configured."
#             if "TODO" not in code_str and len(code_str) > 30:
#                 score = 0.75
#                 reason = "Heuristic: code present and non-trivial."
#             lowered = code_str.lower()
#             if "merge" in lowered or "sort" in lowered:
#                 score = min(0.95, score + 0.1)
#                 reason = reason + " Keyword match increased score."
#             return float(score), reason

#         # LLM path: ask for JSON with score & reason
#         prompt = (
#             "You are a code quality judge. Rate the following code in a JSON object with fields:\n"
#             "  score: float between 0.0 and 1.0 (higher is better)\n"
#             "  reason: short explanation\n\n"
#             f"CODE:\n{code_str}\n\nRespond ONLY with valid JSON."
#         )
#         try:
#             raw = self.client.generate_content(prompt).strip()
#             try:
#                 parsed = json.loads(raw)
#                 score = float(parsed.get("score", 0.0))
#                 reason = parsed.get("reason", raw)
#                 return max(0.0, min(1.0, score)), str(reason)
#             except Exception:
#                 # extract a number if possible
#                 import re
#                 m = re.search(r"([01](?:\.\d+)?)", raw)
#                 if m:
#                     score = float(m.group(1))
#                     return max(0.0, min(1.0, score)), raw
#                 return 0.5, raw
#         except Exception as e:
#             return 0.0, f"LLM error: {e}"

#     def enhance_code(self, code: str) -> str:
#         """
#         Enhance code using LLM if available; else heuristic add-on.
#         """
#         if not self.client:
#             try:
#                 return code + "\n// Enhanced (heuristic): please implement details."
#             except Exception:
#                 return str(code) + "\n// Enhanced (heuristic)."

#         prompt = (
#             "You are a code improver. Improve the following code for correctness, safety, and efficiency.\n"
#             "Return only the improved code.\n\n"
#             f"CODE:\n{code}\n"
#         )
#         try:
#             improved = self.client.generate_content(prompt)
#             return improved
#         except Exception:
#             return code

#     def monitor_agent(self, agent_name: str, payload: Any, field_hint: Optional[str] = None) -> Tuple[Any, Dict]:
#         """
#         Inspect payload (dict or str), pick a target field (by hint or heuristics),
#         judge, and if below threshold call enhance_code repeatedly (max_retries).
#         Returns (possibly modified_payload, log_entry).
#         """
#         # initialize
#         is_data_dict = isinstance(payload, dict)
#         target_key = None
#         value = None

#         # If payload is dict, try to pick the value to monitor
#         if is_data_dict:
#             if field_hint and field_hint in payload:
#                 target_key = field_hint
#                 value = payload.get(target_key)
#             else:
#                 for key in ("code", "reviewed_code", "review", "tests", "analysis", "execution_results"):
#                     if key in payload and payload.get(key) is not None:
#                         target_key = key
#                         value = payload.get(key)
#                         break
#             # If nothing found, stringify the payload
#             if value is None:
#                 try:
#                     orig_text = json.dumps(payload, ensure_ascii=False)
#                 except Exception:
#                     orig_text = str(payload)
#                 target_key = None
#         else:
#             # payload is a plain string or other type
#             value = payload

#         # If target is execution_results (structured), skip judging
#         if target_key == "execution_results":
#             log_entry = {
#                 "agent_name": agent_name,
#                 "skipped": True,
#                 "reason": "execution_results is structured; skipping judge/enhance.",
#                 "payload_excerpt": (str(value)[:200] + "...") if isinstance(value, str) and len(value) > 200 else str(value)
#             }
#             self.logs.append(log_entry)
#             return payload, log_entry

#         # Ensure orig_text exists and is string
#         if value is None:
#             orig_text = ""
#         elif isinstance(value, str):
#             orig_text = value
#         else:
#             try:
#                 orig_text = json.dumps(value, ensure_ascii=False)
#             except Exception:
#                 orig_text = str(value)

#         log_entry = {
#             "agent_name": agent_name,
#             "initial_text_excerpt": (orig_text[:200] + "...") if len(orig_text) > 200 else orig_text,
#             "initial_full_text": orig_text,
#             "enhancement_rounds": []
#         }

#         # initial judgement
#         score, reason = self.judge_code(orig_text)
#         log_entry["initial_personal_score"] = float(score)
#         log_entry["initial_judge_reason"] = reason

#         final_text = orig_text
#         final_score = score
#         final_reason = reason

#         retries = 0
#         while final_score < self.threshold and retries < self.max_retries:
#             improved = self.enhance_code(final_text)
#             new_score, new_reason = self.judge_code(improved)
#             log_entry["enhancement_rounds"].append({
#                 "round": retries + 1,
#                 "enhanced_text_excerpt": (improved[:200] + "...") if len(improved) > 200 else improved,
#                 "enhanced_full_text": improved,
#                 "score": float(new_score),
#                 "judge_reason": new_reason
#             })
#             final_text = improved
#             final_score = new_score
#             final_reason = new_reason
#             retries += 1

#         log_entry["final_personal_score"] = float(final_score)
#         log_entry["final_judge_reason"] = final_reason
#         log_entry["final_full_text"] = final_text

#         # Save log
#         self.logs.append(log_entry)

#         # Put final_text back into payload if it's a dict and we had a target_key
#         if is_data_dict and target_key:
#             payload[target_key] = final_text
#             return payload, log_entry

#         if not is_data_dict:
#             return final_text, log_entry

#         return payload, log_entry

#     def save_run_log(self, run_name: Optional[str] = None) -> str:
#         """
#         Save current self.logs to a JSON file. Returns the saved filepath.
#         """
#         timestamp = run_name or datetime.now().strftime("%Y%m%d_%H%M%S")
#         filepath = os.path.join(self.log_dir, f"run_{timestamp}.json")
#         with open(filepath, "w", encoding="utf-8") as f:
#             json.dump(self.logs, f, indent=2, ensure_ascii=False)
#         print(f"[AgentMonitor] Logs saved to {filepath}")
#         # Clear logs for next run
#         self.logs = []
#         return filepath
# Agent_Monitor/agent_monitor.py
# ... (keep imports and classes as before) ...

# Agent_Monitor/agent_monitor.py

# import os
# import json
# from datetime import datetime
# from typing import Tuple, Any, Dict, Optional

# # Optional import for Gemini LLM; monitor works heuristically if not present
# try:
#     import google.generativeai as genai
# except Exception:
#     genai = None


# class GeminiClientWrapper:
#     def __init__(self, api_key: str):
#         if genai is None:
#             raise RuntimeError("google.generativeai not installed.")
#         genai.configure(api_key=api_key)
#         self.model_name = "gemini-1.5-flash"

#     def generate_content(self, prompt: str) -> str:
#         model = genai.GenerativeModel(self.model_name)
#         resp = model.generate_content(prompt)
#         return getattr(resp, "text", str(resp))


# class AgentMonitor:
#     def __init__(
#         self,
#         api_key: Optional[str] = None,
#         threshold: float = 0.8,
#         max_retries: int = 2,
#         log_dir: str = "Agent_Monitor/logs",
#     ):
#         self.threshold = threshold
#         self.max_retries = max_retries
#         self.log_dir = log_dir
#         os.makedirs(self.log_dir, exist_ok=True)
#         self.logs = []
#         self.client = None
#         if api_key:
#             if genai is None:
#                 raise RuntimeError(
#                     "google.generativeai is not installed in this environment."
#                 )
#             self.client = GeminiClientWrapper(api_key)

#     def judge_code(self, code: Any) -> Tuple[float, str]:
#         """
#         Returns (score in 0..1, reason).
#         Accepts any payload (strings, dicts) — converts to string safely.
#         """
#         if isinstance(code, str):
#             code_str = code
#         else:
#             try:
#                 code_str = json.dumps(code, ensure_ascii=False)
#             except Exception:
#                 code_str = str(code)

#         if not self.client:
#             score = 0.5
#             reason = "Heuristic fallback: no LLM client configured."
#             if "TODO" not in code_str and len(code_str) > 30:
#                 score = 0.75
#                 reason = "Heuristic: code present and non-trivial."
#             lowered = code_str.lower()
#             if "merge" in lowered or "sort" in lowered:
#                 score = min(0.95, score + 0.1)
#                 reason = reason + " Keyword match increased score."
#             return float(score), reason

#         prompt = (
#             "You are a code quality judge. Rate the following code in a JSON object with fields:\n"
#             "  score: float between 0.0 and 1.0 (higher is better)\n"
#             "  reason: short explanation\n\n"
#             f"CODE:\n{code_str}\n\nRespond ONLY with valid JSON."
#         )
#         try:
#             raw = self.client.generate_content(prompt).strip()
#             try:
#                 parsed = json.loads(raw)
#                 score = float(parsed.get("score", 0.0))
#                 reason = parsed.get("reason", raw)
#                 return max(0.0, min(1.0, score)), str(reason)
#             except Exception:
#                 import re

#                 m = re.search(r"([01](?:\.\d+)?)", raw)
#                 if m:
#                     score = float(m.group(1))
#                     return max(0.0, min(1.0, score)), raw
#                 return 0.5, raw
#         except Exception as e:
#             return 0.0, f"LLM error: {e}"

#     def enhance_code(self, code: str) -> str:
#         """
#         Enhance code using LLM if available; else heuristic add-on.
#         """
#         if not self.client:
#             try:
#                 return code + "\n// Enhanced (heuristic): please implement details."
#             except Exception:
#                 return str(code) + "\n// Enhanced (heuristic)."

#         prompt = (
#             "You are a code improver. Improve the following code for correctness, safety, and efficiency.\n"
#             "Return only the improved code.\n\n"
#             f"CODE:\n{code}\n"
#         )
#         try:
#             improved = self.client.generate_content(prompt)
#             return improved
#         except Exception:
#             return code

#     def monitor_agent(
#         self, agent_name: str, payload: Any, field_hint: Optional[str] = None
#     ) -> Tuple[Any, Dict]:
#         """
#         Inspect payload, judge, enhance if needed, return updated payload and minimal log entry.
#         """
#         is_data_dict = isinstance(payload, dict)
#         target_key = None
#         value = None

#         if is_data_dict:
#             if field_hint and field_hint in payload:
#                 target_key = field_hint
#                 value = payload.get(target_key)
#             else:
#                 for key in (
#                     "code",
#                     "reviewed_code",
#                     "review",
#                     "tests",
#                     "analysis",
#                     "execution_results",
#                 ):
#                     if key in payload and payload.get(key) is not None:
#                         target_key = key
#                         value = payload.get(key)
#                         break

#             if value is None:
#                 try:
#                     orig_text = json.dumps(payload, ensure_ascii=False)
#                 except Exception:
#                     orig_text = str(payload)
#                 target_key = None
#         else:
#             value = payload

#         # Skip judging execution_results structured data
#         if target_key == "execution_results":
#             log_entry = {
#                 "agent_name": agent_name,
#                 "initial_score": None,
#                 "initial_code": None,
#                 "final_score": None,
#                 "final_code": None,
#             }
#             self.logs.append(log_entry)
#             return payload, log_entry

#         if value is None:
#             orig_text = ""
#         elif isinstance(value, str):
#             orig_text = value
#         else:
#             try:
#                 orig_text = json.dumps(value, ensure_ascii=False)
#             except Exception:
#                 orig_text = str(value)

#         score, reason = self.judge_code(orig_text)

#         final_text = orig_text
#         final_score = score

#         retries = 0
#         while final_score < self.threshold and retries < self.max_retries:
#             improved = self.enhance_code(final_text)
#             new_score, new_reason = self.judge_code(improved)
#             final_text = improved
#             final_score = new_score
#             retries += 1

#         log_entry = {
#             "agent_name": agent_name,
#             "initial_score": float(score),
#             "initial_code": orig_text,
#             "final_score": float(final_score),
#             "final_code": final_text,
#         }
#         self.logs.append(log_entry)

#         if is_data_dict and target_key:
#             payload[target_key] = final_text
#             return payload, log_entry

#         if not is_data_dict:
#             return final_text, log_entry

#         return payload, log_entry

#     def save_run_log(self, run_name: Optional[str] = None) -> str:
#         """
#         Save current self.logs to a JSON file. Returns the saved filepath.
#         """
#         timestamp = run_name or datetime.now().strftime("%Y%m%d_%H%M%S")
#         filepath = os.path.join(self.log_dir, f"run_{timestamp}.json")
#         with open(filepath, "w", encoding="utf-8") as f:
#             json.dump(self.logs, f, indent=2, ensure_ascii=False)
#         print(f"[AgentMonitor] Logs saved to {filepath}")
#         # Clear logs for next run
#         self.logs = []
#         return filepath

# Agent_Monitor/agent_monitor.py

import os
import json
import time
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
    """
    Monitors each agent output:
      - Extracts multi-indicator scores using LLM (fallback to heuristic)
      - Enhances until threshold on personal_score
      - Logs latency, loops, token_usage
    """

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
        self.client = GeminiClientWrapper(api_key) if api_key else None

    # ---------- LLM scoring prompts ----------
    def _score_multi_llm(self, text: str) -> Dict[str, float]:
        """
        Ask Gemini for structured assessment:
          - personal_score: scored separately for accuracy
          - other indicators: factual_accuracy, clarity, safety, code_correctness, complexity
        Returns dict with float values in [0,1].
        """
        def clamp(x):
            try:
                v = float(x)
                return max(0.0, min(1.0, v))
            except Exception:
                return 0.0

        # 1️⃣ Score personal_score separately
        personal_prompt = (
            "You are an evaluator of code/text quality. "
            "Rate the following content's **overall usefulness and quality** for the user's goal. "
            "Return ONLY a JSON with field 'personal_score' in [0,1].\n\n"
            f"CONTENT:\n{text}"
        )
        try:
            personal_raw = self.client.generate_content(personal_prompt).strip()
            personal_parsed = json.loads(personal_raw)
            personal_score = clamp(personal_parsed.get("personal_score", 0.0))
        except Exception:
            personal_score = 0.0

        # 2️⃣ Score other indicators together
        other_prompt = (
            "You are a precise evaluator. Read the following content (code or text) and "
            "return a compact JSON object with these float fields in [0,1]:\n"
            "  factual_accuracy: correctness of claims or logic\n"
            "  clarity: readability and organization\n"
            "  safety: absence of insecure, harmful, or dangerous patterns\n"
            "  code_correctness: functional soundness (0 if no code)\n"
            "  complexity: implementation complexity (0 simple, 1 very complex)\n"
            "Respond ONLY with JSON and no extra text.\n\n"
            f"CONTENT:\n{text}"
        )
        try:
            other_raw = self.client.generate_content(other_prompt).strip()
            other_parsed = json.loads(other_raw)
        except Exception:
            other_parsed = {}

        return {
            "personal_score": personal_score,
            "factual_accuracy": clamp(other_parsed.get("factual_accuracy", 0.0)),
            "clarity": clamp(other_parsed.get("clarity", 0.0)),
            "safety": clamp(other_parsed.get("safety", 0.0)),
            "code_correctness": clamp(other_parsed.get("code_correctness", 0.0)),
            "complexity": clamp(other_parsed.get("complexity", 0.0)),
        }

    def _score_multi_heuristic(self, text: str) -> Dict[str, float]:
        """
        Heuristic scoring when no LLM client is available.
        Scores personal_score separately from other indicators to mimic LLM separation.
        """
        t = text.lower() if isinstance(text, str) else str(text).lower()
        nontrivial = 1.0 if len(t) > 60 else 0.4
        has_code_hint = any(k in t for k in ["def ", "class ", "{", "};", "public ", "//", "#include", "print(", "function "])
        sorted_hint = any(k in t for k in ["sort", "merge", "binary search", "dp", "graph", "tree"])

        # Personal score separate
        personal = 0.6 * nontrivial + (0.2 if has_code_hint else 0.0) + (0.1 if sorted_hint else 0.0)

        # Other indicators together
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

    # ---------- Enhancement ----------
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

    # ---------- Monitor one agent ----------
    def monitor_agent(
        self, agent_name: str, payload: Any, field_hint: Optional[str] = None
    ) -> Tuple[Any, Dict]:
        """
        Inspect payload, extract indicators, enhance until threshold on personal_score,
        return updated payload and a rich log entry.
        """
        t0 = time.time()

        is_data_dict = isinstance(payload, dict)
        target_key, value = None, None

        if is_data_dict:
            if field_hint and field_hint in payload:
                target_key = field_hint
                value = payload.get(target_key)
            else:
                for key in ("code", "review", "tests", "analysis", "execution_results"):
                    if key in payload and payload.get(key) is not None:
                        target_key = key
                        value = payload.get(key)
                        break
        else:
            value = payload

        # skip judging structured execution_results
        if target_key == "execution_results":
            latency = time.time() - t0
            log_entry = {
                "agent_name": agent_name,
                "initial_code": None,
                "final_code": None,
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
        scores = self._score_multi(text)
        loops = 0
        final_text = text

        # enhance until threshold on personal_score
        while scores["personal_score"] < self.threshold and loops < self.max_retries:
            improved = self._enhance(final_text)
            improved_scores = self._score_multi(improved)

            # accept improvement only if personal_score increases (avoid oscillations)
            if improved_scores["personal_score"] >= scores["personal_score"]:
                final_text = improved
                scores = improved_scores

            loops += 1

        latency = time.time() - t0
        approx_tokens = max(1, len(final_text) // 4)

        log_entry = {
            "agent_name": agent_name,
            "initial_code": text,
            "final_code": final_text,
            "personal_score": float(scores["personal_score"]),
            "factual_accuracy": float(scores["factual_accuracy"]),
            "clarity": float(scores["clarity"]),
            "safety": float(scores["safety"]),
            "code_correctness": float(scores["code_correctness"]),
            "complexity": float(scores["complexity"]),
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

    # ---------- Persist all agent logs ----------
    def save_run_log(self, run_name: Optional[str] = None) -> str:
        timestamp = run_name or datetime.now().strftime("%Y%m%d_%H%M%S")
        filepath = os.path.join(self.log_dir, f"run_{timestamp}.json")
        with open(filepath, "w", encoding="utf-8") as f:
            json.dump(self.logs, f, indent=2, ensure_ascii=False)
        print(f"[AgentMonitor] Logs saved to {filepath}")
        self.logs = []
        return filepath
