# Agent_Monitor/run_with_monitor.py
import os
import sys
import json
import traceback
import time
from datetime import datetime
from dotenv import load_dotenv

load_dotenv()

sys.path.append(os.path.abspath(os.path.join(os.path.dirname(__file__), "..")))

from MAS.mas_pipeline import code_pipeline, qa_pipeline
from Agent_Monitor.agent_monitor import AgentMonitor, GeminiClientWrapper, genai
from Agent_Monitor.feature_aggregator import collect_run_features, append_row, AGENT_ORDER

GEMINI_API_KEY = os.getenv("GEMINI_API_KEY")


def build_gemini_client(api_key: str):
    try:
        return GeminiClientWrapper(api_key)
    except Exception:
        if genai is None:
            raise RuntimeError("google.generativeai not installed.")
        genai.configure(api_key=api_key)
        class _W:
            def __init__(self, model_name="gemini-2.0-flash"):
                self.model_name = model_name
            def generate_content(self, prompt: str) -> str:
                model = genai.GenerativeModel(self.model_name)
                resp = model.generate_content(prompt)
                return getattr(resp, "text", str(resp))
        return _W()


def run_prompt(prompt: str, task_type: str = "auto", api_key: str = None, threshold: float = 0.8, max_retries: int = 2):
    if api_key:
        try:
            llm_client = build_gemini_client(api_key)
        except Exception:
            llm_client = None
    else:
        llm_client = None

    monitor = AgentMonitor(api_key=api_key if api_key else None, threshold=threshold, max_retries=max_retries, log_dir=os.path.join(os.path.dirname(__file__), "..", "logs"))

    if task_type == "code":
        pipeline = code_pipeline(llm_client)
    elif task_type == "qa":
        pipeline = qa_pipeline(llm_client)
    else:
        lower = prompt.lower()
        if any(k in lower for k in ("code", "java", "python", "function", "sort", "merge")):
            pipeline = code_pipeline(llm_client)
        else:
            pipeline = qa_pipeline(llm_client)

    data = {}
    agent_logs = []
    agent_features = {}
    pipeline_edges = []

    try:
        for i, (name, agent, hint) in enumerate(pipeline):
            t_start = time.time()
            if i == 0:
                out = agent.run(prompt)
                if isinstance(out, dict):
                    data.update(out)
                else:
                    data = out
            else:
                out = agent.run(data)
                if isinstance(out, dict):
                    data.update(out)
                else:
                    data = out

            data, log = monitor.monitor_agent(name, data, field_hint=hint)
            agent_logs.append(log)

            score = log.get("personal_score") or log.get("final_personal_score") or 0.0
            loops = log.get("enhancement_loops") or log.get("enhancement_loops") or 0
            latency = log.get("latency")
            if latency is None:
                latency = time.time() - t_start
            tokens = log.get("token_usage") or max(0, len(str(log.get("final_code") or log.get("initial_code") or "")) // 4)

            agent_features[name] = {"personal_score": float(score), "loops": int(loops), "latency": float(latency), "tokens": int(tokens)}
            if i > 0:
                prev_agent = pipeline[i-1][0]
                pipeline_edges.append((prev_agent, name))

    except Exception:
        print("Error during pipeline run:")
        traceback.print_exc()

    run_id = datetime.now().strftime("%Y%m%d_%H%M%S")
    logs_dir = os.path.join(os.path.dirname(__file__), "..", "logs")
    os.makedirs(logs_dir, exist_ok=True)
    raw_log_path = os.path.join(logs_dir, f"run_{run_id}.json")
    with open(raw_log_path, "w", encoding="utf-8") as f:
        json.dump({"agent_logs": agent_logs, "agent_features": agent_features, "graph_edges": pipeline_edges, "prompt": prompt}, f, indent=2, ensure_ascii=False)

    run_state = {"agent_features": agent_features, "graph_edges": pipeline_edges, "prompt": prompt}
    features = collect_run_features(run_state, agent_logs=agent_logs, llm_client=llm_client)

    summary_path = os.path.join(logs_dir, f"summary_{run_id}.json")
    monitor.save_json_summary(filepath=summary_path, collective_score=features.get("collective_score"))

    return data, features, raw_log_path, summary_path


def main():
    print("=== AgentMonitor runner (single prompt) ===")
    prompt = input("Enter your task or prompt: ").strip()
    api_key = os.getenv("GEMINI_API_KEY")
    if not api_key:
        ask = input("No GEMINI_API_KEY in env. Provide one now? (y/N): ").strip().lower()
        if ask == "y":
            api_key = input("Enter GEMINI_API_KEY: ").strip()
        else:
            api_key = None

    data, features, raw_log, summary = run_prompt(prompt, task_type="auto", api_key=api_key)
    print("\n=== Final MAS Output (short) ===")
    for k, v in data.items():
        if isinstance(v, str) and len(v) > 300:
            print(f"{k}: (long text, {len(v)} chars) ...")
        else:
            print(f"{k}: {v}")

    csv_path = os.path.join(os.path.dirname(__file__), "..", "data", "features.csv")
    try:
        append_row(csv_path, features)
        print(f"Features appended to: {os.path.abspath(csv_path)}")
    except Exception as e:
        print("Warning: failed to append CSV row:", e)

    print(f"\nRaw log: {raw_log}")
    print(f"Summary: {summary}")


if __name__ == "__main__":
    main()
