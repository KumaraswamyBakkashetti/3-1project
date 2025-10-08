"""
CSV Analysis - Why columns have repeated values
"""
import pandas as pd
import os

csv_path = "data/features_training_20251008_114454.csv"

# Read CSV
df = pd.read_csv(csv_path)

print("=" * 80)
print("📊 CSV DATA ANALYSIS - Identifying Repeated Values")
print("=" * 80)

print(f"\nTotal rows: {len(df)}")
print(f"Total columns: {len(df.columns)}")

print("\n" + "=" * 80)
print("🔍 COLUMNS WITH CONSTANT (REPEATED) VALUES")
print("=" * 80)

constant_cols = []
for col in df.columns:
    unique_values = df[col].nunique()
    if unique_values <= 3:  # Nearly constant
        constant_cols.append(col)
        print(f"\n📌 {col}:")
        print(f"   Unique values: {unique_values}")
        print(f"   Value distribution:")
        value_counts = df[col].value_counts()
        for val, count in value_counts.items():
            percentage = (count / len(df)) * 100
            print(f"      {val}: {count} times ({percentage:.1f}%)")

print("\n" + "=" * 80)
print("📈 COLUMNS WITH VARYING VALUES")
print("=" * 80)

varying_cols = [col for col in df.columns if col not in constant_cols]
for col in varying_cols:
    unique_values = df[col].nunique()
    print(f"\n✓ {col}:")
    print(f"   Unique values: {unique_values}")
    print(f"   Range: {df[col].min():.3f} to {df[col].max():.3f}")
    print(f"   Mean: {df[col].mean():.3f}")

print("\n" + "=" * 80)
print("🎯 ROOT CAUSE ANALYSIS")
print("=" * 80)

print("\n1️⃣ GRAPH METRICS (Always Same - Expected)")
print("   These are CONSTANT because all runs use the SAME pipeline structure:")
print("   - num_nodes: Always 5 (or 3) agents")
print("   - num_edges: Always 4 (or 2) connections")
print("   - clustering_coefficient: Always 0 (linear pipeline)")
print("   - transitivity: Always 0 (no triangles in linear graph)")
print("   - avg_degree_centrality: Depends on num_nodes")
print("   - avg_betweenness_centrality: Same for same structure")
print("   - avg_closeness_centrality: Same for same structure")
print("   - pagerank_entropy: Same for same structure")
print("   - heterogeneity_score: Same for same structure")

print("\n2️⃣ COLLECTIVE SCORE (Always 0.5 - Problem)")
print("   This is CONSTANT at 0.5 because:")
print("   - LLM collective scoring might be failing")
print("   - Defaulting to 0.5 (neutral score)")
print("   - Check feature_aggregator.py get_collective_score_with_llm()")

print("\n3️⃣ BENCHMARK SCORES (Mostly 0.0 - Expected)")
print("   humaneval_score, gsm8k_score, mmlu_score are 0 or 1 because:")
print("   - Binary evaluation (correct=1.0, incorrect=0.0)")
print("   - Most tasks are failing or not from that benchmark")

print("\n4️⃣ MAX LOOPS (Always 2 - Problem)")
print("   All agents hitting max retries (2):")
print("   - Suggests scores are consistently below threshold (0.8)")
print("   - Enhancement loop always runs maximum iterations")
print("   - May indicate scoring is too harsh or enhancement isn't working")

print("\n" + "=" * 80)
print("💡 RECOMMENDATIONS")
print("=" * 80)

print("\n✅ What's NORMAL (Don't fix):")
print("   - Graph metrics being constant (same pipeline structure)")
print("   - Benchmark scores being 0/1 (binary evaluation)")

print("\n⚠️  What NEEDS FIXING:")
print("   1. Collective score stuck at 0.5")
print("      → Check if LLM is being called in feature_aggregator.py")
print("      → Verify llm_client is being passed correctly")
print("\n   2. All agents hitting max_loops=2")
print("      → Lower threshold from 0.8 to 0.6")
print("      → Or increase max_retries to 3")
print("      → Check if enhancement is actually improving scores")
print("\n   3. Vary the pipeline structure")
print("      → Add different agent combinations")
print("      → Create conditional pipelines")
print("      → This will vary graph metrics")

print("\n" + "=" * 80)
print("🔧 QUICK FIXES")
print("=" * 80)

print("\n1. Check collective_score issue:")
print("   Open: Agent_Monitor/feature_aggregator.py")
print("   Line: ~110 (get_collective_score_with_llm)")
print("   Fix: Ensure llm_client is not None")

print("\n2. Adjust enhancement threshold:")
print("   Open: Agent_Monitor/agent_monitor.py")
print("   Line: ~32 (threshold default)")
print("   Change: threshold=0.8 → threshold=0.6")

print("\n3. Add pipeline variety:")
print("   Open: MAS/mas_pipeline.py")
print("   Add: Different pipelines for different task types")

print("\n" + "=" * 80)
