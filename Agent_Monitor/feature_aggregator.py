# Agent_Monitor/feature_aggregator.py

import networkx as nx
import math
import json
import csv
import os


AGENT_ORDER = [
    "RequirementAnalyzer",
    "CodeGenerator",
    "CodeReviewer",
    "UnitTestWriter",
    "CodeExecutor"
]


def compute_graph_indicators(edges, agents):
    """Compute graph-level features for the multi-agent system."""
    G = nx.DiGraph()
    G.add_nodes_from(agents)
    G.add_edges_from(edges)

    num_nodes = G.number_of_nodes()
    num_edges = G.number_of_edges()
    clustering = nx.average_clustering(G.to_undirected()) if num_nodes > 1 else 0.0
    transitivity = nx.transitivity(G.to_undirected()) if num_nodes > 2 else 0.0

    degree_centrality = nx.degree_centrality(G)
    betweenness = nx.betweenness_centrality(G)
    closeness = nx.closeness_centrality(G) if num_nodes > 1 else {a: 0.0 for a in agents}
    pagerank = nx.pagerank(G) if num_nodes > 0 else {a: 0.0 for a in agents}

    avg_deg = sum(degree_centrality.values()) / num_nodes if num_nodes else 0.0
    avg_betw = sum(betweenness.values()) / num_nodes if num_nodes else 0.0
    avg_close = sum(closeness.values()) / num_nodes if num_nodes else 0.0

    pr_vals = list(pagerank.values())
    pagerank_entropy = -sum(p*math.log(p, 2) for p in pr_vals if p > 0)

    mean_pr = sum(pr_vals) / len(pr_vals) if pr_vals else 0
    heterogeneity_score = sum((p - mean_pr)**2 for p in pr_vals) / len(pr_vals) if pr_vals else 0

    return {
        "num_nodes": num_nodes,
        "num_edges": num_edges,
        "clustering_coefficient": clustering,
        "transitivity": transitivity,
        "avg_degree_centrality": avg_deg,
        "avg_betweenness_centrality": avg_betw,
        "avg_closeness_centrality": avg_close,
        "pagerank_entropy": pagerank_entropy,
        "heterogeneity_score": heterogeneity_score,
    }

def get_collective_score_with_llm(agent_logs, llm_client=None):
    """
    Uses LLM to judge overall collective performance of MAS agents.
    Expects agent_logs = list of dicts from AgentMonitor.
    """
    if not llm_client:
        return 0.5  # fallback if no LLM configured

    # Build a compact JSON summary for the LLM
    summary = []
    for log in agent_logs or []:
        summary.append({
            "agent_name": log.get("agent_name"),
            "final_score": log.get("final_score"),
            "final_code": (log.get("final_code") or "")[:200]  # safe truncation
        })

    prompt = (
        "You are an evaluator of a multi-agent system. "
        "Based on the following agents' outputs and scores, "
        "give a single JSON with field:\n"
        "  collective_score: float between 0 and 1 (higher = better teamwork & output quality).\n\n"
        f"AGENT LOGS:\n{json.dumps(summary, indent=2)}\n\n"
        "Respond ONLY with JSON."
    )

    try:
        raw = llm_client.generate_content(prompt).strip()
        print("DEBUG: LLM raw response:", raw)
        parsed = json.loads(raw)
        print("DEBUG: Parsed LLM response:", parsed)
        return float(parsed.get("collective_score", 0.5))
    except Exception as e:
        print("DEBUG: Exception in collective score LLM call:", e)
        return 0.5


def collect_run_features(run_state, agent_logs=None, llm_client=None):
    """
    Aggregates system-level + graph-level indicators + collective score.
    run_state should have:
      - agent_features: dict {agent_name: {scores, latency, loops, tokens}}
      - graph_edges: list of (agent_from, agent_to)
    agent_logs: list of logs from AgentMonitor (used for LLM collective score)
    """
    agent_features = run_state.get("agent_features", {})
    edges = run_state.get("graph_edges", [])

    # System-level features
    scores = [f.get("personal_score", 0.0) for f in agent_features.values()]
    latencies = [f.get("latency", 0.0) for f in agent_features.values()]
    loops = [f.get("loops", 0) for f in agent_features.values()]
    tokens = [f.get("tokens", 0) for f in agent_features.values()]

    avg_score = sum(scores) / len(scores) if scores else 0.0
    min_score = min(scores) if scores else 0.0
    max_loops = max(loops) if loops else 0
    total_latency = sum(latencies)
    total_tokens = sum(tokens)
    triggered = sum(1 for f in agent_features.values() if f.get("loops", 0) > 0)

    system_feats = {
        "avg_personal_score": avg_score,
        "min_personal_score": min_score,
        "max_loops": max_loops,
        "total_latency": total_latency,
        "total_token_usage": total_tokens,
        "num_agents_triggered_enhancement": triggered,
    }

    # Graph-level features using actual agents in this run
    agents_in_run = list(agent_features.keys())
    graph_feats = compute_graph_indicators(edges, agents_in_run)

    # Collective score from LLM
    collective_score = get_collective_score_with_llm(agent_logs, llm_client)

    # Merge all features
    features = {}
    features.update(system_feats)
    features.update(graph_feats)
    features["collective_score"] = collective_score

    return features

def append_row(csv_path: str, features: dict):
    """
    Append the features dict as a row to a CSV file.
    If file does not exist, write header first.
    Ensures consistent columns for all runs.
    """
    os.makedirs(os.path.dirname(csv_path), exist_ok=True)

    # Define consistent CSV columns
    fieldnames = [
        "avg_personal_score", "min_personal_score", "max_loops",
        "total_latency", "total_token_usage", "num_agents_triggered_enhancement",
        "num_nodes", "num_edges", "clustering_coefficient", "transitivity",
        "avg_degree_centrality", "avg_betweenness_centrality", "avg_closeness_centrality",
        "pagerank_entropy", "heterogeneity_score", "collective_score"
    ]

    # Prepare row with default values if keys missing
    row = {k: features.get(k, 0) for k in fieldnames}

    file_exists = os.path.isfile(csv_path)
    with open(csv_path, "a", newline="", encoding="utf-8") as f:
        writer = csv.DictWriter(f, fieldnames=fieldnames)
        if not file_exists:
            writer.writeheader()
        writer.writerow(row)
