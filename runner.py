import time
import json  # for safe serialization
from judge import JudgeLLM
from enhancer import CodeEnhancer
from agents import RequirementAnalyzer, CodeGenerator, CodeReviewer, UnitTestWriter, CodeExecutor
from utils import safe_score

# Global state
features = []
edges = []  # ✅ track communication edges
THRESHOLD = 80


def run_agent_with_scoring(agent, input_data, agent_name, next_agent_name=None):
    """
    Run an agent, score its output, and log an edge to the next agent.
    """
    start_time = time.time()
    loops = 0
    flags = []

    # Run the agent
    output_data = agent.run(input_data)

    # Collect content to score
    if isinstance(output_data, dict) or isinstance(output_data, list):
        content_to_score = json.dumps(output_data)  # serialize dict/list safely
    else:
        content_to_score = str(output_data)

    # Judge & enhance if below threshold
    judge = JudgeLLM()
    enhancer = CodeEnhancer()
    score = safe_score(judge, content_to_score)

    while score < THRESHOLD and loops < 3:
        content_to_score = enhancer.improve(content_to_score)
        score = safe_score(judge, content_to_score)
        loops += 1

    elapsed_time = round(time.time() - start_time, 2)
    token_usage = len(content_to_score.split())

    # ✅ Save metrics with personal score
    features.append({
        "agent": agent_name,
        "personal_score": score,
        "output": content_to_score,  # store serialized output
        "loops": loops,
        "runtime": elapsed_time,
        "token_usage": token_usage,
        "flags": flags
    })

    # ✅ Log edge from this agent → next agent
    if next_agent_name:
        edges.append((agent_name, next_agent_name))

    print(f"[{agent_name}] Final Score: {score} | Loops: {loops} | Runtime: {elapsed_time}s")
    return output_data


def get_features():
    return features


def get_edges():
    return edges


# --- MAS wrapper ---
def run_mas_and_extract_metrics(prompt):
    """
    Runs the full MAS pipeline on a single prompt and returns:
    - feature_summary: dict with metrics for each agent
    - final_output: the last agent’s output
    - edges: list of (agent_i, agent_j) tuples representing communication
    """
    pipeline = [
        RequirementAnalyzer(),
        CodeGenerator(),
        CodeReviewer(),
        UnitTestWriter(),
        CodeExecutor()
    ]

    # Reset global state for each run
    global features, edges
    features = []
    edges = []

    data = prompt
    for i, agent in enumerate(pipeline):
        agent_name = f"Agent {i+1} - {agent.__class__.__name__}"
        next_agent_name = f"Agent {i+2} - {pipeline[i+1].__class__.__name__}" if i < len(pipeline) - 1 else None
        data = run_agent_with_scoring(agent, data, agent_name, next_agent_name)

    # Compute feature summary
    feature_summary = {}
    for f in get_features():
        # ✅ Ensure data is a string before concatenation
        final_data_str = json.dumps(data) if isinstance(data, (dict, list)) else str(data)
        collective_score = safe_score(JudgeLLM(), f["output"] + "\n" + final_data_str)
        feature_summary[f["agent"]] = {
            "personal_score": f["personal_score"],
            "collective_score": collective_score,
            "loops": f["loops"],
            "runtime": f["runtime"],
            "token_usage": f["token_usage"]
        }

    return feature_summary, data, get_edges()
