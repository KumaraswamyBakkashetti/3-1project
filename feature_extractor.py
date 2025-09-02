def extract_features(agent_metrics, benchmark_scores):
    """
    Aggregate agent-level metrics for compatibility with graph-level features.
    Expects `agent_metrics` to be a list of dicts, each dict containing agent info.
    """

    if not agent_metrics:
        return {
            "Avg_Score": None,
            "Total_Loops": 0,
            "Total_Runtime": 0,
            "Num_Agents": 0,
            **benchmark_scores
        }

    # Handle the case where agent_metrics is a single dict (convert to list)
    if isinstance(agent_metrics, dict):
        agent_metrics = [agent_metrics]

    num_agents = len(agent_metrics)

    avg_score = sum(a.get('score', 0) for a in agent_metrics) / num_agents
    total_loops = sum(a.get('loops', 0) for a in agent_metrics)
    total_runtime = sum(a.get('runtime', 0) for a in agent_metrics)

    features = {
        "Avg_Score": avg_score,
        "Total_Loops": total_loops,
        "Total_Runtime": total_runtime,
        "Num_Agents": num_agents,
    }

    # Include any benchmark scores if provided
    features.update(benchmark_scores)

    return features
