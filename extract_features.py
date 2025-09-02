import pandas as pd
import os
import time
import json  # for safe serialization of dicts/lists
import google.api_core.exceptions  # for quota handling
from runner import run_mas_and_extract_metrics  # MAS runner
from feature_extractor import extract_features  # updated aggregation function

mmlu_data = []
test_data = []

# Helper to safely serialize nested dicts/lists
def safe_serialize(value):
    if isinstance(value, (dict, list)):
        return json.dumps(value)
    return value

# Loop through datasets
for dataset_name in ["mmlu", "humaneval", "gsm8k"]:
    dataset_path = f"data/{dataset_name}/data.csv"
    if not os.path.exists(dataset_path):
        print(f"❌ Dataset not found: {dataset_path}")
        continue

    df = pd.read_csv(dataset_path)

    # ⚠️ Optional: Limit rows for debugging/quota control
    df = df.head(1)

    for _, row in df.iterrows():
        # ----- Build prompt depending on dataset -----
        if dataset_name == "mmlu":
            prompt = f"Question: {row['question']}\nChoices: {row['choices']}"
        else:
            prompt = row.get("prompt", row.get("question", ""))

        # ----- Run MAS to extract agent metrics, final output, edges -----
        try:
            agent_metrics, final_output, edges = run_mas_and_extract_metrics(prompt)
        except google.api_core.exceptions.ResourceExhausted:
            print("⚠️ API quota exhausted, skipping this row...")
            continue
        except Exception as e:
            print(f"❌ Error processing row: {e}")
            continue

        # ----- Handle targets (for MMLU only) -----
        if dataset_name == "mmlu":
            mas_pred = agent_metrics.get("prediction", None)
            gold_answer = row["answer"]
            target_score = (
                int(str(mas_pred).strip() == str(gold_answer).strip()) if mas_pred else None
            )
        else:
            target_score = None

        # ----- Aggregate agent + graph features -----
        aggregated_features = extract_features(agent_metrics, benchmark_scores={})

        # ----- Ensure edges stored as stringified list -----
        edges_str = json.dumps(edges) if edges else "[]"

        # ----- Build row -----
        row_data = {
            "dataset": dataset_name,
            "prompt": prompt,
            "final_output": safe_serialize(final_output),
            "edges": edges_str,
            "target": target_score,
        }

        # Add gold answer only for MMLU
        if dataset_name == "mmlu":
            row_data["answer"] = row["answer"]

        # Add per-agent personal & collective scores
        for agent_name, metrics in agent_metrics.items():
            row_data[f"{agent_name}_personal_score"] = metrics.get("personal_score")
            row_data[f"{agent_name}_collective_score"] = metrics.get("collective_score")

        # Add aggregated graph/network features
        serialized_features = {k: safe_serialize(v) for k, v in aggregated_features.items()}
        row_data.update(serialized_features)

        # ----- Append to train vs test -----
        if dataset_name == "mmlu":
            mmlu_data.append(row_data)
        else:
            test_data.append(row_data)

# ----- Save separate train/test files -----
mmlu_path = "data/mmlu_train.csv"
test_path = "data/test_features.csv"

pd.DataFrame(mmlu_data).to_csv(mmlu_path, index=False)
pd.DataFrame(test_data).to_csv(test_path, index=False)

print(f"✅ Training file saved: {mmlu_path} ({len(mmlu_data)} rows)")
print(f"✅ Testing file saved: {test_path} ({len(test_data)} rows)")
