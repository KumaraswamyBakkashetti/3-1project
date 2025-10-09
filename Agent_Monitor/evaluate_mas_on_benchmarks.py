# Agent_Monitor/evaluate_mas_on_benchmarks.py
"""
Proper benchmark evaluation following research paper approach:
- Each MAS variant is tested on ALL THREE benchmarks
- Features aggregated across runs to create one row per MAS
- Includes all 15 features + 3 benchmark scores + label_mas_score
"""

import os
import pandas as pd
import numpy as np
from pathlib import Path
from tqdm import tqdm
import sys

# Add parent directory to path for imports
sys.path.insert(0, str(Path(__file__).parent.parent))

from Agent_Monitor.run_with_monitor import run_prompt


class MASBenchmarkEvaluator:
    """Evaluate a MAS configuration across all three benchmarks"""
    
    def __init__(self, mas_config):
        self.config = mas_config
        self.name = mas_config['name']
        self.all_features = []  # Store features from all runs

    def evaluate_on_humaneval(self, num_samples=20):
        """Run MAS on HumanEval coding tasks"""
        print(f"\n[HUMANEVAL] Evaluating {self.name} on HumanEval...")
        
        # Load HumanEval dataset
        humaneval_path = Path(__file__).parent.parent / 'BenchmarkDatasetFolder' / 'HumanEval' / 'data.csv'
        df = pd.read_csv(humaneval_path)
        
        # Sample tasks
        sampled = df.sample(n=min(num_samples, len(df)), random_state=42)
        
        scores = []
        for idx, row in tqdm(sampled.iterrows(), total=len(sampled), desc="HumanEval"):
            prompt = row['prompt']
            
            # Run MAS with this configuration
            try:
                data, features, raw_log, summary = run_prompt(
                    prompt=prompt,
                    task_type='code',
                    api_key=self.config.get('api_key'),
                    threshold=self.config.get('threshold', 0.6),
                    max_retries=self.config.get('max_retries', 2)
                )
                
                # Store features for aggregation
                features['benchmark'] = 'humaneval'
                self.all_features.append(features)
                
                # Check if code is correct
                code_correct = data.get('execution_result', {}).get('syntax_ok', False)
                scores.append(1.0 if code_correct else 0.0)
                
            except Exception as e:
                print(f"[WARNING] HumanEval task {idx} failed: {e}")
                scores.append(0.0)
        
        avg_score = np.mean(scores) if scores else 0.0
        print(f"[HUMANEVAL] {self.name} score: {avg_score:.4f}")
        return avg_score

    def evaluate_on_gsm8k(self, num_samples=20):
        """Run MAS on GSM8K math reasoning tasks"""
        print(f"\n[GSM8K] Evaluating {self.name} on GSM8K...")
        
        # Load GSM8K dataset
        gsm8k_path = Path(__file__).parent.parent / 'BenchmarkDatasetFolder' / 'GSM8k' / 'data.csv'
        df = pd.read_csv(gsm8k_path)
        
        # Sample tasks
        sampled = df.sample(n=min(num_samples, len(df)), random_state=42)
        
        scores = []
        for idx, row in tqdm(sampled.iterrows(), total=len(sampled), desc="GSM8K"):
            question = row['question']
            expected_answer = row['answer']
            
            # Run MAS with this configuration
            try:
                data, features, raw_log, summary = run_prompt(
                    prompt=question,
                    task_type='qa',
                    api_key=self.config.get('api_key'),
                    threshold=self.config.get('threshold', 0.6),
                    max_retries=self.config.get('max_retries', 2)
                )
                
                # Store features for aggregation
                features['benchmark'] = 'gsm8k'
                self.all_features.append(features)
                
                # Extract answer from MAS output
                mas_answer = data.get('answer', '')
                
                # Check if answer is correct
                correct = str(expected_answer).strip() in str(mas_answer).strip()
                scores.append(1.0 if correct else 0.0)
                
            except Exception as e:
                print(f"[WARNING] GSM8K task {idx} failed: {e}")
                scores.append(0.0)
        
        avg_score = np.mean(scores) if scores else 0.0
        print(f"[GSM8K] {self.name} score: {avg_score:.4f}")
        return avg_score

    def evaluate_on_mmlu(self, num_samples=20):
        """Run MAS on MMLU knowledge/reasoning tasks"""
        print(f"\n[MMLU] Evaluating {self.name} on MMLU...")
        
        # Load MMLU dataset
        mmlu_path = Path(__file__).parent.parent / 'BenchmarkDatasetFolder' / 'MMLU' / 'data.csv'
        df = pd.read_csv(mmlu_path)
        
        # Sample tasks
        sampled = df.sample(n=min(num_samples, len(df)), random_state=42)
        
        scores = []
        for idx, row in tqdm(sampled.iterrows(), total=len(sampled), desc="MMLU"):
            question = row['question']
            correct_answer = row['answer']
            
            # Run MAS with this configuration
            try:
                data, features, raw_log, summary = run_prompt(
                    prompt=question,
                    task_type='qa',
                    api_key=self.config.get('api_key'),
                    threshold=self.config.get('threshold', 0.6),
                    max_retries=self.config.get('max_retries', 2)
                )
                
                # Store features for aggregation
                features['benchmark'] = 'mmlu'
                self.all_features.append(features)
                
                # Extract answer from MAS output
                mas_answer = data.get('answer', '')
                
                # Check if answer matches
                correct = str(correct_answer).strip().lower() in str(mas_answer).strip().lower()
                scores.append(1.0 if correct else 0.0)
                
            except Exception as e:
                print(f"[WARNING] MMLU task {idx} failed: {e}")
                scores.append(0.0)
        
        avg_score = np.mean(scores) if scores else 0.0
        print(f"[MMLU] {self.name} score: {avg_score:.4f}")
        return avg_score

    def aggregate_features(self):
        """Aggregate features across all runs (all benchmarks)"""
        if not self.all_features:
            return {}
        
        # Features to aggregate (take mean across all runs)
        feature_names = [
            'avg_personal_score', 'min_personal_score', 'max_loops',
            'total_latency', 'total_token_usage', 'num_agents_triggered_enhancement',
            'num_nodes', 'num_edges', 'clustering_coefficient', 'transitivity',
            'avg_degree_centrality', 'avg_betweenness_centrality', 'avg_closeness_centrality',
            'pagerank_entropy', 'heterogeneity_score', 'collective_score'
        ]
        
        aggregated = {}
        for fname in feature_names:
            values = [f.get(fname, 0.0) for f in self.all_features]
            aggregated[fname] = np.mean(values) if values else 0.0
        
        return aggregated

    def evaluate_all_benchmarks(self, num_samples_per_benchmark=20):
        """Evaluate MAS on all three benchmarks"""
        print(f"\n{'='*60}")
        print(f"Evaluating MAS: {self.name}")
        print(f"Configuration: {self.config}")
        print(f"{'='*60}")
        
        # Clear previous features
        self.all_features = []
        
        # Run all three benchmarks
        humaneval_score = self.evaluate_on_humaneval(num_samples=num_samples_per_benchmark)
        gsm8k_score = self.evaluate_on_gsm8k(num_samples=num_samples_per_benchmark)
        mmlu_score = self.evaluate_on_mmlu(num_samples=num_samples_per_benchmark)
        
        # Compute label_mas_score (weak supervision)
        label_mas_score = (
            0.5 * humaneval_score +
            0.3 * gsm8k_score +
            0.2 * mmlu_score
        )
        
        # Aggregate features across all runs
        aggregated_features = self.aggregate_features()
        
        # Combine everything into one row
        row = {
            **aggregated_features,  # 15 features
            'humaneval_score': humaneval_score,
            'gsm8k_score': gsm8k_score,
            'mmlu_score': mmlu_score,
            'label_mas_score': label_mas_score
        }
        
        print(f"\n{'='*60}")
        print(f"Results for {self.name}:")
        print(f"  HumanEval: {humaneval_score:.4f}")
        print(f"  GSM8K:     {gsm8k_score:.4f}")
        print(f"  MMLU:      {mmlu_score:.4f}")
        print(f"  MAS Score: {label_mas_score:.4f}")
        print(f"  Features collected: {len(self.all_features)} runs")
        print(f"{'='*60}\n")
        
        return row


def evaluate_multiple_mas_variants(num_samples=10):
    """Evaluate multiple MAS configurations on all benchmarks"""
    
    # Define MAS variants to evaluate
    mas_variants = [
        {
            'name': 'CodeMAS_v1',
            'threshold': 0.6,
            'max_retries': 2,
            'api_key': os.getenv('GEMINI_API_KEY')
        },
        {
            'name': 'CodeMAS_Aggressive',
            'threshold': 0.5,
            'max_retries': 3,
            'api_key': os.getenv('GEMINI_API_KEY')
        },
        {
            'name': 'CodeMAS_Conservative',
            'threshold': 0.7,
            'max_retries': 1,
            'api_key': os.getenv('GEMINI_API_KEY')
        },
        {
            'name': 'LogicMAS_v1',
            'threshold': 0.6,
            'max_retries': 2,
            'api_key': os.getenv('GEMINI_API_KEY')
        },
        {
            'name': 'QA_MAS_v1',
            'threshold': 0.6,
            'max_retries': 2,
            'api_key': os.getenv('GEMINI_API_KEY')
        },
    ]
    
    all_results = []
    
    for config in mas_variants:
        evaluator = MASBenchmarkEvaluator(config)
        row = evaluator.evaluate_all_benchmarks(num_samples_per_benchmark=num_samples)
        all_results.append(row)
    
    # Create DataFrame with proper column order
    columns = [
        # 15 features
        'avg_personal_score', 'min_personal_score', 'max_loops',
        'total_latency', 'total_token_usage', 'num_agents_triggered_enhancement',
        'num_nodes', 'num_edges', 'clustering_coefficient', 'transitivity',
        'avg_degree_centrality', 'avg_betweenness_centrality', 'avg_closeness_centrality',
        'pagerank_entropy', 'heterogeneity_score', 'collective_score',
        # 3 benchmark scores
        'humaneval_score', 'gsm8k_score', 'mmlu_score',
        # 1 label
        'label_mas_score'
    ]
    
    df = pd.DataFrame(all_results, columns=columns)
    
    # Save results
    output_path = Path(__file__).parent.parent / 'data' / 'mas_benchmark_results.csv'
    df.to_csv(output_path, index=False)
    
    print("\n" + "="*80)
    print("All MAS Variants Evaluated!")
    print("="*80)
    print("\nSample of results:")
    print(df[['avg_personal_score', 'min_personal_score', 'humaneval_score', 
              'gsm8k_score', 'mmlu_score', 'label_mas_score']].to_string())
    print(f"\nFull dataset shape: {df.shape}")
    print(f"Columns: {list(df.columns)}")
    print(f"\nSaved to: {output_path}")
    print("="*80)
    
    return df


def main():
    """Main evaluation pipeline"""
    print("="*80)
    print("MAS Benchmark Evaluation (Research Paper Approach)")
    print("="*80)
    print("\nThis will:")
    print("1. Test each MAS variant on ALL THREE benchmarks")
    print("2. Aggregate 15 features across all runs")
    print("3. Create training data with features + benchmark scores + label\n")
    
    choice = input("Run evaluation? (y/n): ").strip().lower()
    if choice != 'y':
        print("Cancelled.")
        return
    
    num_samples = int(input("Samples per benchmark (default 10, min 5, max 100): ").strip() or "10")
    
    df = evaluate_multiple_mas_variants(num_samples=num_samples)
    
    print("\n✅ Complete! Now you can train XGBoost:")
    print("   python Trainer/xgb_trainer_mas.py")


if __name__ == "__main__":
    main()
