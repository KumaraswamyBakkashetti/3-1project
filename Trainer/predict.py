# Trainer/predict.py
import os
import joblib
import pandas as pd
import numpy as np

ROOT = os.path.abspath(os.path.join(os.path.dirname(__file__), ".."))
MODEL_PATH = os.path.join(ROOT, "models", "xgb_model.joblib")


def predict_from_features(features: dict):
    if not os.path.exists(MODEL_PATH):
        raise FileNotFoundError("Model not found. Train first with Trainer/xgb_trainer.py")

    saved = joblib.load(MODEL_PATH)
    model = saved["model"]
    cols = saved["columns"]
    # Build dataframe row
    row = {c: float(features.get(c, 0.0)) for c in cols}
    df = pd.DataFrame([row], columns=cols)
    pred = model.predict(df.values)[0]
    return float(pred)


if __name__ == "__main__":
    # simple interactive example
    sample = {
        "avg_personal_score": 0.7,
        "min_personal_score": 0.4,
        "max_loops": 1,
        "total_latency": 5.0,
        "total_token_usage": 1200,
        "num_agents_triggered_enhancement": 1,
        "num_nodes": 5,
        "num_edges": 4,
        "clustering_coefficient": 0.0,
        "transitivity": 0.0,
        "avg_degree_centrality": 0.2,
        "avg_betweenness_centrality": 0.05,
        "avg_closeness_centrality": 0.3,
        "pagerank_entropy": 2.1,
        "heterogeneity_score": 0.01,
        "collective_score": 0.0,
        "humaneval_score": 0.5,
        "gsm8k_score": 0.5,
        "mmlu_score": 0.5
    }
    print("Prediction:", predict_from_features(sample))
