# Safe Benchmark Runner - Handles file locking issues
# Creates timestamped CSV files to avoid conflicts

import os
import time
from datetime import datetime
from Agent_Monitor.benchmark_runner import read_dataset, evaluate_humaneval_output, evaluate_qa_output
from Agent_Monitor.run_with_monitor import run_prompt
from Agent_Monitor.feature_aggregator import append_row

ROOT = os.path.abspath(os.path.join(os.path.dirname(__file__), ".", ))
BENCH_DIR = os.path.join(ROOT, "BenchmarkDatasetFolder")
DATA_DIR = os.path.join(ROOT, "data")

def run_bench_safe(bench_name: str, api_key: str, max_examples: int, output_csv: str):
    """Run benchmark with safe file handling"""
    print(f"[bench_runner] Running benchmark: {bench_name}")
    
    rows = read_dataset(bench_name)
    if not rows:
        print("[bench_runner] no rows found")
        return
    
    count = 0
    for r in rows:
        prompt = r.get("prompt") or r.get("question") or r.get("input") or ""
        gold = r.get("answer") or r.get("gold") or r.get("reference") or None
        task_type = "code" if bench_name.lower().startswith("humaneval") else "qa"
        
        print(f"\n[{count+1}/{max_examples}] Processing: {prompt[:50]}...")
        
        try:
            data, features, raw_log, summary = run_prompt(prompt, task_type=task_type, api_key=api_key)
            
            if bench_name.lower().startswith("humaneval"):
                score = evaluate_humaneval_output(data, gold)
                features["humaneval_score"] = score
            elif bench_name.lower().startswith("gsm8k"):
                score = evaluate_qa_output(data, gold, api_key)
                features["gsm8k_score"] = score
            elif bench_name.lower().startswith("mmlu"):
                score = evaluate_qa_output(data, gold, api_key)
                features["mmlu_score"] = score
            else:
                score = evaluate_qa_output(data, gold, api_key)
            
            # Try to append, retry if file is locked
            max_retries = 3
            for attempt in range(max_retries):
                try:
                    append_row(output_csv, features)
                    break
                except PermissionError:
                    if attempt < max_retries - 1:
                        print(f"⚠️  File locked, retrying in 2 seconds... (attempt {attempt+1}/{max_retries})")
                        time.sleep(2)
                    else:
                        print(f"❌ Error: Could not write to {output_csv}")
                        print("   Please close the file in Excel/editor and press Enter to retry...")
                        input()
                        append_row(output_csv, features)
            
            count += 1
            print(f"✅ Completed {count}/{max_examples}")
            
            if max_examples and count >= max_examples:
                break
                
        except Exception as e:
            print(f"❌ Error processing example: {e}")
            continue
    
    print(f"[bench_runner] Completed {count} examples for {bench_name}")


if __name__ == "__main__":
    api_key = os.getenv("GEMINI_API_KEY")
    
    # Create timestamped output file to avoid conflicts
    timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
    output_csv = os.path.join(DATA_DIR, f"features_training_{timestamp}.csv")
    
    print("=" * 70)
    print("🚀 SAFE TRAINING DATA GENERATION")
    print("=" * 70)
    print(f"\nOutput file: {output_csv}")
    print("\nThis will run 20 examples from each benchmark.")
    print("Total: 60 rows of training data")
    print("Estimated time: 30-60 minutes")
    print("\n⚠️  You can open/view the CSV file while this runs!")
    print("=" * 70)
    
    response = input("\nProceed? (y/n): ").strip().lower()
    if response != 'y':
        print("Cancelled.")
        exit(0)
    
    # Run limited examples from each benchmark
    benchmarks = [
        ("HumanEval", 20),  # 20 code generation tasks
        ("GSM8K", 20),       # 20 math reasoning tasks
        ("MMLU", 20)         # 20 knowledge tasks
    ]
    
    total_start = time.time()
    
    for bench_name, max_examples in benchmarks:
        print(f"\n{'='*70}")
        print(f"📊 Running {bench_name} - {max_examples} examples")
        print(f"{'='*70}")
        run_bench_safe(bench_name, api_key=api_key, max_examples=max_examples, output_csv=output_csv)
    
    total_time = time.time() - total_start
    
    print("\n" + "=" * 70)
    print("✅ COMPLETE! Training data generated.")
    print("=" * 70)
    print(f"\n📁 Output file: {output_csv}")
    print(f"⏱️  Total time: {total_time/60:.1f} minutes")
    print("\nNext steps:")
    print("  1. Merge this file with features.csv:")
    print(f"     type {output_csv} >> data\\features.csv")
    print("\n  2. Train model:")
    print("     python Trainer/xgb_trainer.py")
    print("\n  3. Check your data:")
    print(f"     type {output_csv}")
