# Agent_Monitor/run_with_monitor.py
import os
import sys
from datetime import datetime
import traceback
import json
from dotenv import load_dotenv

load_dotenv()

sys.path.append(os.path.abspath(os.path.join(os.path.dirname(__file__), "..")))
#api_key = os.getenv("GEMINI_API_KEY")

from MAS.mas_pipeline import RequirementAnalyzer, CodeGenerator, CodeReviewer, UnitTestWriter, CodeExecutor
from Agent_Monitor.agent_monitor import AgentMonitor, GeminiClientWrapper, genai


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


def main():
    print("=== AgentMonitor runner (LLM-enabled) ===")
    user_prompt = input("Enter your coding task: ").strip()

    api_key = os.getenv("GEMINIAI_API_KEY")
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
    collective_scores = {}  # Initialize a dictionary to store collective scores

    try:
        name, agent, hint = pipeline[0]
        data = agent.run(user_prompt)
        data, log = monitor.monitor_agent(name, data, field_hint=hint)
        log['agent_name'] = name  # Add agent name to the log
        print(f"\n[Agent: {name}] Initial score: {log['initial_score']}")
        print(f"Initial code:\n{log['initial_code']}\n")
        print(f"[Agent: {name}] Final score: {log['final_score']}")
        print(f"Final code:\n{log['final_code']}\n")

        agent_logs.append(log)
        collective_scores[name] = log['final_score']  # Store the final score

        for name, agent, hint in pipeline[1:]:
            print(f"\n[Agent: {name}] Running...")
            data = agent.run(data)
            data, log = monitor.monitor_agent(name, data, field_hint=hint)
            log['agent_name'] = name  # Add agent name to the log
            print(f"\n[Agent: {name}] Initial score: {log['initial_score']}")
            print(f"Initial code:\n{log['initial_code']}\n")
            print(f"[Agent: {name}] Final score: {log['final_score']}")
            print(f"Final code:\n{log['final_code']}\n")

            agent_logs.append(log)
            collective_scores[name] = log['final_score']  # Store the final score

    except Exception:
        print("Error during pipeline run:")
        traceback.print_exc()

    # Save minimal logs JSON with only agent_name, initial/final scores & codes
    run_id = datetime.now().strftime("%Y%m%d_%H%M%S")
    log_path = os.path.join(os.path.dirname(__file__), "logs", f"run_{run_id}.json")
    os.makedirs(os.path.dirname(log_path), exist_ok=True)

    # Add collective score to each agent's log
    for log in agent_logs:
        agent_name = log['agent_name']
        log['collective_score'] = collective_scores.get(agent_name)  # Get the collective score

    with open(log_path, "w", encoding="utf-8") as f:
        json.dump(agent_logs, f, indent=2, ensure_ascii=False)

    print(f"\n=== Final MAS Output ===")
    for k, v in data.items():
        if isinstance(v, str) and len(v) > 500:
            print(f"{k}: (long text, {len(v)} chars) ...")
        else:
            print(f"{k}: {v}")

    print(f"\nLogs saved to: {log_path}")


if __name__ == "__main__":
    main()