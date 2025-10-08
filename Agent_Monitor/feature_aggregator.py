# Agent_Monitor/feature_aggregator.py
import networkx as nx
import math
import json
import csv
import os
from typing import List, Dict, Any, Optional

AGENT_ORDER = [
    "RequirementAnalyzer",
    "CodeGenerator",
    "CodeReviewer",
    "UnitTestWriter",
    "CodeExecutor"
]


def compute_graph_indicators(edges: List[tuple], agents: List[str]) -> Dict[str, float]:
    G = nx.DiGraph()
    G.add_nodes_from(agents)
    G.add_edges_from(edges)

    num_nodes = G.number_of_nodes()
    num_edges = G.number_of_edges()
    clustering = nx.average_clustering(G.to_undirected()) if num_nodes > 1 else 0.0
    transitivity = nx.transitivity(G.to_undirected()) if num_nodes > 2 else 0.0

    degree_centrality = nx.degree_centrality(G) if num_nodes > 0 else {a: 0.0 for a in agents}
    betweenness = nx.betweenness_centrality(G) if num_nodes > 0 else {a: 0.0 for a in agents}
    closeness = nx.closeness_centrality(G) if num_nodes > 1 else {a: 0.0 for a in agents}
    pagerank = nx.pagerank(G) if num_nodes > 0 else {a: 0.0 for a in agents}

    avg_deg = sum(degree_centrality.values()) / num_nodes if num_nodes else 0.0
    avg_betw = sum(betweenness.values()) / num_nodes if num_nodes else 0.0
    avg_close = sum(closeness.values()) / num_nodes if num_nodes else 0.0

    pr_vals = list(pagerank.values())
    pagerank_entropy = -sum(p * math.log(p, 2) for p in pr_vals if p > 0) if pr_vals else 0.0

    mean_pr = sum(pr_vals) / len(pr_vals) if pr_vals else 0.0
    heterogeneity_score = sum((p - mean_pr) ** 2 for p in pr_vals) / len(pr_vals) if pr_vals else 0.0

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


def get_collective_score_with_llm(agent_logs: List[Dict[str, Any]], llm_client=None) -> float:
    if not llm_client:
        print("[WARNING] No LLM client provided for collective score, using 0.5")
        return 0.5
    
    def extract_json(raw_text: str) -> str:
        """Extract JSON from markdown code blocks if present"""
        raw_text = raw_text.strip()
        if raw_text.startswith("```json"):
            raw_text = raw_text[7:]
        elif raw_text.startswith("```"):
            raw_text = raw_text[3:]
        if raw_text.endswith("```"):
            raw_text = raw_text[:-3]
        return raw_text.strip()
    
    summary = []
    for log in agent_logs or []:
        summary.append({
            "agent_name": log.get("agent_name"),
            "final_personal_score": log.get("final_personal_score"),
            "final_code": (log.get("final_code") or "")[:300]
        })
    prompt = (
        "You are an evaluator of a multi-agent system. "
        "Given the following agents' outputs and final scores, return JSON with field:\n"
        "  collective_score: float between 0 and 1.\n\n"
        f"AGENT LOGS:\n{json.dumps(summary, indent=2)}\n\nRespond ONLY with JSON."
    )
    try:
        raw = llm_client.generate_content(prompt).strip()
        raw = extract_json(raw)
        parsed = json.loads(raw)
        score = float(parsed.get("collective_score", 0.5))
        print(f"[INFO] Collective score from LLM: {score}")
        return score
    except Exception as e:
        print(f"[WARNING] Failed to get collective score from LLM: {e}, using 0.5")
        return 0.5


def collect_run_features(run_state: Dict[str, Any], agent_logs: Optional[List[Dict[str, Any]]] = None, llm_client=None) -> Dict[str, Any]:
    agent_features = run_state.get("agent_features", {})
    edges = run_state.get("graph_edges", [])

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

    agents_in_run = list(agent_features.keys())
    graph_feats = compute_graph_indicators(edges, agents_in_run)
    collective_score = get_collective_score_with_llm(agent_logs, llm_client)

    # Benchmarks if present in run_state
    humaneval = run_state.get("humaneval_score", 0.0)
    gsm8k = run_state.get("gsm8k_score", 0.0)
    mmlu = run_state.get("mmlu_score", 0.0)

    features = {}
    features.update(system_feats)
    features.update(graph_feats)
    features["collective_score"] = collective_score
    features["humaneval_score"] = humaneval
    features["gsm8k_score"] = gsm8k
    features["mmlu_score"] = mmlu

    return features


def append_row(csv_path: str, features: Dict[str, Any]):
    os.makedirs(os.path.dirname(csv_path), exist_ok=True)
    fieldnames = [
        "avg_personal_score", "min_personal_score", "max_loops",
        "total_latency", "total_token_usage", "num_agents_triggered_enhancement",
        "num_nodes", "num_edges", "clustering_coefficient", "transitivity",
        "avg_degree_centrality", "avg_betweenness_centrality", "avg_closeness_centrality",
        "pagerank_entropy", "heterogeneity_score", "collective_score",
        "humaneval_score", "gsm8k_score", "mmlu_score"
    ]
    row = {k: features.get(k, 0) for k in fieldnames}
    file_exists = os.path.isfile(csv_path)
    with open(csv_path, "a", newline="", encoding="utf-8") as f:
        writer = csv.DictWriter(f, fieldnames=fieldnames)
        if not file_exists:
            writer.writeheader()
        writer.writerow(row)
