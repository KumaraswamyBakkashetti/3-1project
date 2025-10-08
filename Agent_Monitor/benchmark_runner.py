# Agent_Monitor/benchmark_runner.py
import os
import csv
import json
from typing import Optional
from Agent_Monitor.run_with_monitor import run_prompt
from Agent_Monitor.feature_aggregator import append_row

ROOT = os.path.abspath(os.path.join(os.path.dirname(__file__), ".."))
BENCH_DIR = os.path.join(ROOT, "BenchmarkDatasetFolder")
OUT_CSV = os.path.join(ROOT, "data", "features.csv")


def read_dataset(bench_name: str):
    path = os.path.join(BENCH_DIR, bench_name, "data.csv")
    if not os.path.exists(path):
        print(f"[bench_runner] dataset missing: {path}")
        return []
    rows = []
    with open(path, newline='', encoding='utf-8') as f:
        reader = csv.DictReader(f)
        for r in reader:
            rows.append(r)
    return rows


def evaluate_humaneval_output(data: dict, answer: Optional[str]) -> float:
    exec_res = data.get("execution_results", {})
    if exec_res.get("note") == "syntax_ok" or exec_res.get("passed", 0) > 0:
        return 1.0
    return 0.0


def evaluate_qa_output(final_data: dict, gold_answer: Optional[str], llm_key: Optional[str]) -> float:
    final_answer = final_data.get("answer") or final_data.get("final_code") or ""
    if not gold_answer:
        return 0.5
    if llm_key:
        from Agent_Monitor.agent_monitor import GeminiClientWrapper
        try:
            client = GeminiClientWrapper(llm_key)
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
    else:
        return 1.0 if final_answer.strip().lower() == gold_answer.strip().lower() else 0.0


def run_bench(bench_name: str, api_key: Optional[str] = None, max_examples: Optional[int] = None):
    print(f"[bench_runner] Running benchmark: {bench_name}")
    rows = read_dataset(bench_name)
    if not rows:
        print("[bench_runner] no rows found")
        return
    count = 0
    for r in rows:
        prompt = r.get("prompt") or r.get("question") or r.get("input") or ""
        gold = r.get("answer") or r.get("gold") or r.get("reference") or None
        task_type = "code" if bench_name.lower().startswith("humaneval") else "qa"
        data, features, raw_log, summary = run_prompt(prompt, task_type=task_type, api_key=api_key)
        if bench_name.lower().startswith("humaneval"):
            score = evaluate_humaneval_output(data, gold)
            features["humaneval_score"] = score
        elif bench_name.lower().startswith("gsm8k"):
            score = evaluate_qa_output(data, gold, api_key)
            features["gsm8k_score"] = score
        elif bench_name.lower().startswith("mmlu"):
            score = evaluate_qa_output(data, gold, api_key)
            features["mmlu_score"] = score
        else:
            score = evaluate_qa_output(data, gold, api_key)
        append_row(OUT_CSV, features)
        count += 1
        if max_examples and count >= max_examples:
            break
    print(f"[bench_runner] Completed {count} examples for {bench_name}")


if __name__ == "__main__":
    key = os.getenv("GEMINI_API_KEY")
    for bench in ("HumanEval", "GSM8K", "MMLU"):
        run_bench(bench, api_key=key, max_examples=None)
