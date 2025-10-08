# Agent_Monitor/utils/eval_utils.py
import json
from typing import Optional
from Agent_Monitor.agent_monitor import GeminiClientWrapper
import os

def llm_compare_answers(final_answer: str, gold_answer: str, api_key: Optional[str] = None) -> float:
    if not api_key:
        return 1.0 if final_answer.strip().lower() == gold_answer.strip().lower() else 0.0
    try:
        client = GeminiClientWrapper(api_key)
        prompt = (
            "You are an evaluator. Given a final answer and a gold (reference) answer, "
            "return ONLY JSON {\"score\": <0..1>} where 1.0 = correct.\n\n"
            f"FINAL_ANSWER:\n{final_answer}\n\nGOLD_ANSWER:\n{gold_answer}\n\nRespond ONLY with JSON."
        )
        raw = client.generate_content(prompt).strip()
        parsed = json.loads(raw)
        return float(parsed.get("score", 0.0))
    except Exception:
        return 1.0 if final_answer.strip().lower() == gold_answer.strip().lower() else 0.0
