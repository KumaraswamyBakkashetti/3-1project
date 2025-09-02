import networkx as nx
import pandas as pd
import ast  # to parse edges stored as strings
import numpy as np

def build_graph(edges):
    """Build directed graph from MAS communication edges (list of tuples)"""
    G = nx.DiGraph()
    G.add_edges_from(edges)
    return G

def compute_graph_indicators(G):
    """Compute aggregated graph-level indicators"""
    indicators = {}

    # Degree centrality
    deg = list(nx.degree_centrality(G).values())
    indicators["deg_mean"] = np.mean(deg)
    indicators["deg_sum"] = np.sum(deg)
    indicators["deg_max"] = np.max(deg)
    indicators["deg_min"] = np.min(deg)

    # Betweenness centrality
    bet = list(nx.betweenness_centrality(G).values())
    indicators["bet_mean"] = np.mean(bet)
    indicators["bet_sum"] = np.sum(bet)
    indicators["bet_max"] = np.max(bet)
    indicators["bet_min"] = np.min(bet)

    # Closeness centrality
    close = list(nx.closeness_centrality(G).values())
    indicators["close_mean"] = np.mean(close)
    indicators["close_sum"] = np.sum(close)
    indicators["close_max"] = np.max(close)
    indicators["close_min"] = np.min(close)

    # Clustering coefficient (convert to undirected)
    clust = list(nx.clustering(G.to_undirected()).values())
    indicators["clust_mean"] = np.mean(clust)
    indicators["clust_sum"] = np.sum(clust)
    indicators["clust_max"] = np.max(clust)
    indicators["clust_min"] = np.min(clust)

    # PageRank
    pr = list(nx.pagerank(G).values())
    indicators["pr_mean"] = np.mean(pr)
    indicators["pr_sum"] = np.sum(pr)
    indicators["pr_max"] = np.max(pr)
    indicators["pr_min"] = np.min(pr)

    # Graph-level metrics
    indicators["transitivity"] = nx.transitivity(G.to_undirected())
    indicators["num_nodes"] = G.number_of_nodes()
    indicators["num_edges"] = G.number_of_edges()

    return indicators

def append_graph_features(csv_path, out_path):
    df = pd.read_csv(csv_path)
    all_features = []

    for _, row in df.iterrows():
        # Parse edges
        try:
            edges = ast.literal_eval(row["edges"]) if "edges" in row else []
        except Exception:
            edges = []

        # Build graph + compute indicators
        G = build_graph(edges)
        features = compute_graph_indicators(G)

        # Keep original fields
        features["dataset"] = row.get("dataset", "")
        features["prompt"] = row.get("prompt", "")
        features["target"] = row.get("target", "")
        features["final_output"] = row.get("final_output", "")

        # ✅ Add LLM agent scores if present in CSV
        features["personal_score"] = row.get("personal_score", np.nan)
        features["collective_score"] = row.get("collective_score", np.nan)

        all_features.append(features)

    # Save to CSV
    feat_df = pd.DataFrame(all_features)
    feat_df.to_csv(out_path, index=False)
    print(f"✅ Saved aggregated graph features to {out_path}")

if __name__ == "__main__":
    # Training (MMLU)
    append_graph_features("data/mmlu_train.csv", "data/mmlu_train_with_graph.csv")

    # Testing (HumanEval + GSM8K)
    append_graph_features("data/test_features.csv", "data/test_with_graph.csv")
