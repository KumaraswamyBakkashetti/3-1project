from dotenv import load_dotenv
from pathlib import Path
import os
import google.generativeai as genai

from agents import (
    RequirementAnalyzer,
    CodeGenerator,
    CodeReviewer,
    UnitTestWriter,
    CodeExecutor
)
from runner import run_agent_with_scoring, get_features

# Load env
env_path = Path(r"C:\Users\FALCON JNP\Documents\AgentMonitor\.env")
load_dotenv(dotenv_path=env_path)

# Configure Gemini API
api_key = os.getenv("GEMINI_API_KEY")
if not api_key:
    raise ValueError("❌ GEMINI_API_KEY not found in environment variables.")
genai.configure(api_key=api_key)

if __name__ == "__main__":
    user_prompt = input("Enter your coding task: ")

    pipeline = [
        RequirementAnalyzer(),
        CodeGenerator(),
        CodeReviewer(),
        UnitTestWriter(),
        CodeExecutor()
    ]

    data = user_prompt
    for i, agent in enumerate(pipeline):
        agent_name = f"Agent {i+1} - {agent.__class__.__name__}"
        data = run_agent_with_scoring(agent, data, agent_name)

    print("\n=== Agent Metrics ===")
    for f in get_features():
        print(f)
