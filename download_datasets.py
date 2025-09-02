from datasets import load_dataset
import pandas as pd
import os

# Create directories if they don't exist
os.makedirs("data/humaneval", exist_ok=True)
os.makedirs("data/mmlu", exist_ok=True)
os.makedirs("data/gsm8k", exist_ok=True)

# 1. HumanEval
humaneval = load_dataset("openai_humaneval",cache_dir="./data_cache")
pd.DataFrame(humaneval['test']).to_csv("data/humaneval/data.csv", index=False)

# 2. MMLU
mmlu= load_dataset("cais/mmlu", "abstract_algebra",cache_dir="./data_cache")
pd.DataFrame(mmlu['test']).to_csv("data/mmlu/data.csv", index=False)

# 3. GSM8K
gsm8k = load_dataset("gsm8k", "main",cache_dir="./data_cache")
pd.DataFrame(gsm8k['test']).to_csv("data/gsm8k/data.csv", index=False)

print("✅ All datasets saved in /data folder")
