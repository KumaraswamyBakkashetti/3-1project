# # Agent_Monitor/run_with_monitor.py
# import os
# import sys
# from datetime import datetime
# import traceback

# # ensure project root on path so we can import MAS and Agent_Monitor
# sys.path.append(os.path.abspath(os.path.join(os.path.dirname(__file__), "..")))

# from MAS.mas_pipeline import RequirementAnalyzer, CodeGenerator, CodeReviewer, UnitTestWriter, CodeExecutor
# from Agent_Monitor.agent_monitor import AgentMonitor, GeminiClientWrapper, genai  # genai may be None

# def build_gemini_client(api_key: str):
#     """
#     Create a GeminiClientWrapper if agent_monitor has it available.
#     If agent_monitor didn't expose GeminiClientWrapper, we attempt a fallback wrapper here.
#     """
#     try:
#         # Use the wrapper defined in agent_monitor module if present
#         return GeminiClientWrapper(api_key)
#     except Exception as e:
#         # If the wrapper isn't available for some reason, try inline creation
#         if genai is None:
#             raise RuntimeError("google.generativeai is not installed; cannot create Gemini client.")
#         genai.configure(api_key=api_key)
#         class _Wrapper:
#             def __init__(self, model_name="gemini-1.5-flash"):
#                 self.model_name = model_name
#             def generate_content(self, prompt: str) -> str:
#                 model = genai.GenerativeModel(self.model_name)
#                 resp = model.generate_content(prompt)
#                 return getattr(resp, "text", str(resp))
#         return _Wrapper()

# def main():
#     print("=== AgentMonitor runner (LLM-enabled) ===")
#     user_prompt = input("Enter your coding task: ").strip()

#     # Try to get GEMINI_API_KEY from env; if not present ask once
#     api_key = os.getenv("GEMINI_API_KEY")
#     if not api_key:
#         ask = input("No GEMINI_API_KEY in env. Do you want to enter one now? (y/N): ").strip().lower()
#         if ask == "y":
#             api_key = input("Enter GEMINI_API_KEY: ").strip()
#         else:
#             api_key = None

#     # Create AgentMonitor - it will create its own client if api_key provided
#     monitor = AgentMonitor(api_key=api_key, threshold=0.8, max_retries=2,
#                            log_dir=os.path.join(os.path.dirname(__file__), "logs"))

#     # Create a Gemini client wrapper to pass into MAS agents (if api_key provided)
#     llm_client = None
#     if api_key:
#         try:
#             llm_client = build_gemini_client(api_key)
#             print("[Runner] Gemini client created and will be passed to MAS agents.")
#         except Exception as e:
#             print("[Runner] Failed to create Gemini client:", e)
#             print("[Runner] Continuing with no LLM client (offline/dummy outputs).")
#             llm_client = None
#     else:
#         print("[Runner] No API key provided — running MAS in offline (dummy) mode; monitor will use heuristics.")

#     # instantiate MAS agents and pass llm_client where applicable
#     analyzer = RequirementAnalyzer(llm=llm_client)
#     generator = CodeGenerator(llm=llm_client)
#     reviewer = CodeReviewer(llm=llm_client)
#     tester = UnitTestWriter(llm=llm_client)
#     executor = CodeExecutor()  # KEEP simulated for safety

#     pipeline = [
#         ("RequirementAnalyzer", analyzer, "analysis"),
#         ("CodeGenerator", generator, "code"),
#         ("CodeReviewer", reviewer, "review"),
#         ("UnitTestWriter", tester, "tests"),
#         ("CodeExecutor", executor, "execution_results")
#     ]

#     data = {}
#     try:
#         # Agent 1: pass prompt string explicitly
#         name, agent, hint = pipeline[0]
#         data = agent.run(user_prompt)
#         data, log = monitor.monitor_agent(name, data, field_hint=hint)
#         print(f"[Monitor] {name} initial score: {log.get('initial_personal_score')}, final score: {log.get('final_personal_score')}")

#         # subsequent agents
#         for name, agent, hint in pipeline[1:]:
#             print(f"\n[Agent: {name}] Running...")
#             data = agent.run(data)
#             data, log = monitor.monitor_agent(name, data, field_hint=hint)
#             print(f"[Monitor] {name} initial score: {log.get('initial_personal_score')}, final score: {log.get('final_personal_score')}")

#     except Exception as e:
#         print("Error during pipeline run:")
#         traceback.print_exc()

#     # Save logs (agent_monitor.save_run_log clears logs in the monitor)
#     log_file = monitor.save_run_log()
#     print("\n=== Final MAS Output ===")
#     for k, v in data.items():
#         if isinstance(v, str) and len(v) > 500:
#             print(f"{k}: (long text, {len(v)} chars) ...")
#         else:
#             print(f"{k}: {v}")

#     print(f"\nLogs written to: {log_file}")

# if __name__ == "__main__":
#     main()

# # Agent_Monitor/run_with_monitor.py
# import os
# import sys
# from datetime import datetime
# import traceback
# import json
# from dotenv import load_dotenv

# load_dotenv()  # This reads variables from .env into os.environ

# api_key = os.getenv("GEMINI_API_KEY")


# sys.path.append(os.path.abspath(os.path.join(os.path.dirname(__file__), "..")))

# from MAS.mas_pipeline import RequirementAnalyzer, CodeGenerator, CodeReviewer, UnitTestWriter, CodeExecutor
# from Agent_Monitor.agent_monitor import AgentMonitor, GeminiClientWrapper, genai


# def build_gemini_client(api_key: str):
#     try:
#         return GeminiClientWrapper(api_key)
#     except Exception as e:
#         if genai is None:
#             raise RuntimeError("google.generativeai is not installed; cannot create Gemini client.")
#         genai.configure(api_key=api_key)
#         class _Wrapper:
#             def __init__(self, model_name="gemini-1.5-flash"):
#                 self.model_name = model_name
#             def generate_content(self, prompt: str) -> str:
#                 model = genai.GenerativeModel(self.model_name)
#                 resp = model.generate_content(prompt)
#                 return getattr(resp, "text", str(resp))
#         return _Wrapper()


# def main():
#     print("=== AgentMonitor runner (LLM-enabled) ===")
#     user_prompt = input("Enter your coding task: ").strip()

#     api_key = os.getenv("GEMINI_API_KEY")
#     if not api_key:
#         ask = input("No GEMINI_API_KEY in env. Enter one now? (y/N): ").strip().lower()
#         if ask == "y":
#             api_key = input("Enter GEMINI_API_KEY: ").strip()
#         else:
#             api_key = None

#     monitor = AgentMonitor(api_key=api_key, threshold=0.8, max_retries=2,
#                            log_dir=os.path.join(os.path.dirname(__file__), "logs"))

#     llm_client = None
#     if api_key:
#         try:
#             llm_client = build_gemini_client(api_key)
#             print("[Runner] Gemini client created and passed to MAS agents.")
#         except Exception as e:
#             print("[Runner] Failed to create Gemini client:", e)
#             print("[Runner] Running MAS offline with dummy outputs.")
#             llm_client = None
#     else:
#         print("[Runner] No API key provided — running MAS offline (dummy outputs).")

#     analyzer = RequirementAnalyzer(llm=llm_client)
#     generator = CodeGenerator(llm=llm_client)
#     reviewer = CodeReviewer(llm=llm_client)
#     tester = UnitTestWriter(llm=llm_client)
#     executor = CodeExecutor()

#     pipeline = [
#         ("RequirementAnalyzer", analyzer, "analysis"),
#         ("CodeGenerator", generator, "code"),
#         ("CodeReviewer", reviewer, "review"),
#         ("UnitTestWriter", tester, "tests"),
#         ("CodeExecutor", executor, "execution_results")
#     ]

#     data = {}
#     agent_logs = []

#     try:
#         name, agent, hint = pipeline[0]
#         data = agent.run(user_prompt)
#         data, log = monitor.monitor_agent(name, data, field_hint=hint)

#         print(f"\n[Agent: {name}] Initial score: {log['initial_score']}")
#         print(f"Initial code:\n{log['initial_code']}\n")
#         print(f"[Agent: {name}] Final score: {log['final_score']}")
#         print(f"Final code:\n{log['final_code']}\n")

#         agent_logs.append(log)

#         for name, agent, hint in pipeline[1:]:
#             print(f"\n[Agent: {name}] Running...")
#             data = agent.run(data)
#             data, log = monitor.monitor_agent(name, data, field_hint=hint)

#             print(f"\n[Agent: {name}] Initial score: {log['initial_score']}")
#             print(f"Initial code:\n{log['initial_code']}\n")
#             print(f"[Agent: {name}] Final score: {log['final_score']}")
#             print(f"Final code:\n{log['final_code']}\n")

#             agent_logs.append(log)

#     except Exception:
#         print("Error during pipeline run:")
#         traceback.print_exc()

#     # Save minimal logs JSON with only agent_name, initial/final scores & codes
#     run_id = datetime.now().strftime("%Y%m%d_%H%M%S")
#     log_path = os.path.join(os.path.dirname(__file__), "logs", f"run_{run_id}.json")
#     os.makedirs(os.path.dirname(log_path), exist_ok=True)
#     with open(log_path, "w", encoding="utf-8") as f:
#         json.dump(agent_logs, f, indent=2, ensure_ascii=False)

#     print(f"\n=== Final MAS Output ===")
#     for k, v in data.items():
#         if isinstance(v, str) and len(v) > 500:
#             print(f"{k}: (long text, {len(v)} chars) ...")
#         else:
#             print(f"{k}: {v}")

#     print(f"\nLogs saved to: {log_path}")


# if __name__ == "__main__":
#     main()

# Agent_Monitor/run_with_monitor.py
# Agent_Monitor/run_with_monitor.py
import os
import sys
from datetime import datetime
import traceback
import json
from dotenv import load_dotenv
import time

load_dotenv()  # Load API key from .env if present

sys.path.append(os.path.abspath(os.path.join(os.path.dirname(__file__), "..")))

from MAS.mas_pipeline import RequirementAnalyzer, CodeGenerator, CodeReviewer, UnitTestWriter, CodeExecutor
from Agent_Monitor.agent_monitor import AgentMonitor, GeminiClientWrapper, genai
from Agent_Monitor.feature_aggregator import collect_run_features, append_row, AGENT_ORDER


def build_gemini_client(api_key: str):
    try:
        return GeminiClientWrapper(api_key)
    except Exception as e:
        if genai is None:
            raise RuntimeError("google.generativeai is not installed; cannot create Gemini client.")
        genai.configure(api_key=api_key)

        class _Wrapper:
            def __init__(self, model_name="gemini-1.5-flash"):
                self.model_name = model_name

            def generate_content(self, prompt: str) -> str:
                model = genai.GenerativeModel(self.model_name)
                resp = model.generate_content(prompt)
                return getattr(resp, "text", str(resp))

        return _Wrapper()


def safe_get_score_from_log(log):
    """Return the best available numeric score from a monitor log."""
    for key in ("personal_score", "final_score", "initial_score", "score"):
        v = log.get(key)
        if isinstance(v, (int, float)):
            return float(v)
        try:
            return float(v)
        except Exception:
            continue
    return 0.0


def safe_get_loops_from_log(log):
    for key in ("enhancement_loops", "enhancement_loops", "loops", "retry_count"):
        v = log.get(key)
        try:
            return int(v)
        except Exception:
            continue
    return 0


def safe_get_latency_from_log(log):
    for key in ("latency", "time_taken", "duration"):
        v = log.get(key)
        try:
            return float(v)
        except Exception:
            continue
    return None


def safe_get_tokens_from_log(log):
    for key in ("token_usage", "tokens", "token_count"):
        v = log.get(key)
        try:
            return int(v)
        except Exception:
            continue
    return None


def pretty_print_log_summary(log):
    # print whatever fields are present, in a small summary
    keys = ["agent_name", "personal_score", "initial_score", "final_score", "enhancement_loops", "latency", "token_usage"]
    summary = {k: log.get(k) for k in keys if k in log}
    return summary


def main():
    print("=== AgentMonitor runner (robust) ===")
    user_prompt = input("Enter your coding task: ").strip()

    api_key = os.getenv("GEMINI_API_KEY")
    if not api_key:
        ask = input("No GEMINI_API_KEY in env. Enter one now? (y/N): ").strip().lower()
        if ask == "y":
            api_key = input("Enter GEMINI_API_KEY: ").strip()
        else:
            api_key = None

    monitor = AgentMonitor(api_key=api_key, threshold=0.8, max_retries=2,
                           log_dir=os.path.join(os.path.dirname(__file__), "logs"))

    llm_client = None
    if api_key:
        try:
            llm_client = build_gemini_client(api_key)
            print("[Runner] Gemini client created and passed to MAS agents.")
        except Exception as e:
            print("[Runner] Failed to create Gemini client:", e)
            print("[Runner] Running MAS offline with dummy outputs.")
            llm_client = None
    else:
        print("[Runner] No API key provided — running MAS offline (dummy outputs).")

    analyzer = RequirementAnalyzer(llm=llm_client)
    generator = CodeGenerator(llm=llm_client)
    reviewer = CodeReviewer(llm=llm_client)
    tester = UnitTestWriter(llm=llm_client)
    executor = CodeExecutor()

    pipeline = [
        ("RequirementAnalyzer", analyzer, "analysis"),
        ("CodeGenerator", generator, "code"),
        ("CodeReviewer", reviewer, "review"),
        ("UnitTestWriter", tester, "tests"),
        ("CodeExecutor", executor, "execution_results")
    ]

    data = {}
    agent_logs = []
    agent_features = {}
    pipeline_edges = []

    try:
        for i, (name, agent, hint) in enumerate(pipeline):
            print(f"\n[Agent: {name}] Running...")
            t_start = time.time()
            if i == 0:
                data = agent.run(user_prompt)
            else:
                data = agent.run(data)

            # Monitor the agent (this may modify data in-place)
            data, log = monitor.monitor_agent(name, data, field_hint=hint)

            # Robust printing: don't assume specific keys exist
            summary = pretty_print_log_summary(log)
            print(f"[Agent summary] {summary}")

            # Ensure agent_logs gets the log even if it lacks some fields
            agent_logs.append(log)

            # Build agent_features entry robustly using available keys
            score = safe_get_score_from_log(log)
            loops = safe_get_loops_from_log(log)
            latency = safe_get_latency_from_log(log)
            if latency is None:
                latency = time.time() - t_start  # fallback if monitor didn't record latency
            tokens = safe_get_tokens_from_log(log)
            if tokens is None:
                # approximate token count from final_code or initial_code text
                txt = log.get("final_code") or log.get("initial_code") or ""
                tokens = max(0, len(str(txt)) // 4)

            agent_features[name] = {
                "personal_score": score,
                "loops": loops,
                "latency": latency,
                "tokens": tokens
            }

            # Build pipeline edges
            if i > 0:
                prev_agent = pipeline[i - 1][0]
                pipeline_edges.append((prev_agent, name))

    except Exception:
        print("Error during pipeline run:")
        traceback.print_exc()

    # Save raw agent logs JSON
    run_id = datetime.now().strftime("%Y%m%d_%H%M%S")
    log_path = os.path.join(os.path.dirname(__file__), "logs", f"run_{run_id}.json")
    os.makedirs(os.path.dirname(log_path), exist_ok=True)
    with open(log_path, "w", encoding="utf-8") as f:
        json.dump({"agent_logs": agent_logs, "agent_features": agent_features, "graph_edges": pipeline_edges}, f, indent=2, ensure_ascii=False)
    print(f"\nLogs saved to: {log_path}")

    # === Collect indicators using LLM-only collective score ===
    run_state = {
        "agent_features": agent_features,
        "graph_edges": pipeline_edges,
        "prompt": user_prompt
    }

    print("DEBUG: llm_client is", llm_client)
    # Call the aggregator which will call LLM for collective_score when llm_client provided
    features = collect_run_features(run_state, agent_logs=agent_logs, llm_client=llm_client)

    # Append to CSV (create data dir if needed)
    csv_path = os.path.join(os.path.dirname(__file__), "..", "data", "features.csv")
    try:
        append_row(csv_path, features)
        print(f"Features appended to: {os.path.abspath(csv_path)}")
    except Exception as e:
        print("Warning: failed to append CSV row:", e)

    # Print final output summary and indicators
    print("\n=== Final MAS Output (short) ===")
    for k, v in data.items():
        if isinstance(v, str) and len(v) > 300:
            print(f"{k}: (long text, {len(v)} chars) ...")
        else:
            print(f"{k}: {v}")

    print("\n=== Indicators ===")
    for k, v in features.items():
        print(f"{k}: {v}")


if __name__ == "__main__":
    main()
