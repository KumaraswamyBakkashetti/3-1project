# Agent_Monitor/utils/graph_utils.py
import networkx as nx
from typing import List, Tuple
import matplotlib.pyplot as plt
import os

def draw_graph(edges: List[Tuple[str, str]], out_path: str):
    G = nx.DiGraph()
    G.add_edges_from(edges)
    plt.figure(figsize=(6,4))
    pos = nx.spring_layout(G)
    nx.draw(G, pos, with_labels=True, node_size=800, arrowsize=20)
    os.makedirs(os.path.dirname(out_path), exist_ok=True)
    plt.savefig(out_path)
    plt.close()
