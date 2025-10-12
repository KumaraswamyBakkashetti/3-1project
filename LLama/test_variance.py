"""
Quick test to verify variance in features
Generates 5 samples and checks if features vary
"""
import asyncio
import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).parent))

from main import run_mas_with_monitoring, extract_features, estimate_code_quality

async def test_variance():
    """Test that features have variance across multiple runs"""
    
    print("="*70)
    print("TESTING VARIANCE IN FEATURES")
    print("="*70)
    print()
    
    tasks = [
        "Write a function to calculate factorial",
        "Write a function to check if number is prime",
        "Write a function to reverse a string",
        "Write a function to find fibonacci number",
        "Write a function to sort a list"
    ]
    
    all_features = []
    all_scores = []
    
    for i, task in enumerate(tasks, 1):
        print(f"\n[Test {i}/5] {task}")
        print("-"*70)
        
        try:
            # Run MAS with monitoring
            result, monitor_data = await run_mas_with_monitoring(task, None)
            
            # Extract features
            features = extract_features(monitor_data)
            all_features.append(features)
            
            # Get quality scores
            code_output = result if isinstance(result, str) else str(result)
            scores = estimate_code_quality(code_output)
            all_scores.append(scores)
            
            print(f"✅ Features extracted: {len(features)}")
            print(f"   num_nodes: {features['num_nodes']}")
            print(f"   num_edges: {features['num_edges']}")
            print(f"   avg_personal_score: {features['avg_personal_score']:.3f}")
            print(f"   HumanEval score: {scores['humaneval_score']:.3f}")
            
        except Exception as e:
            print(f"❌ Error: {e}")
            import traceback
            traceback.print_exc()
            continue
    
    # Analyze variance
    print("\n" + "="*70)
    print("VARIANCE ANALYSIS")
    print("="*70)
    
    if len(all_features) < 2:
        print("❌ Not enough samples to check variance")
        return
    
    # Check key features for variance
    features_to_check = [
        'num_nodes',
        'num_edges', 
        'avg_personal_score',
        'min_personal_score',
        'max_loops',
        'num_agents_triggered_enhancement'
    ]
    
    variance_results = {}
    
    for feat in features_to_check:
        values = [f[feat] for f in all_features]
        unique_count = len(set(values))
        min_val = min(values)
        max_val = max(values)
        
        variance_results[feat] = {
            'unique': unique_count,
            'min': min_val,
            'max': max_val,
            'all_same': unique_count == 1
        }
        
        if unique_count == 1:
            print(f"❌ {feat}: CONSTANT (all = {values[0]})")
        else:
            print(f"✅ {feat}: VARIES ({unique_count} unique, range: {min_val}-{max_val})")
    
    # Check benchmark scores
    print("\nBenchmark Scores:")
    he_scores = [s['humaneval_score'] for s in all_scores]
    gsm_scores = [s['gsm8k_score'] for s in all_scores]
    
    print(f"   HumanEval: {min(he_scores):.3f} - {max(he_scores):.3f} ({len(set(he_scores))} unique)")
    print(f"   GSM8K: {min(gsm_scores):.3f} - {max(gsm_scores):.3f} ({len(set(gsm_scores))} unique)")
    
    # Overall assessment
    print("\n" + "="*70)
    constant_features = sum(1 for v in variance_results.values() if v['all_same'])
    varying_features = len(variance_results) - constant_features
    
    print(f"Constant features: {constant_features}/{len(variance_results)}")
    print(f"Varying features: {varying_features}/{len(variance_results)}")
    
    if constant_features > len(variance_results) / 2:
        print("\n❌ TOO MANY CONSTANT FEATURES - Need more variance!")
    elif constant_features > 0:
        print("\n⚠️ SOME CONSTANT FEATURES - Could improve")
    else:
        print("\n✅ ALL FEATURES HAVE VARIANCE - Excellent!")
    
    print("="*70)

if __name__ == "__main__":
    asyncio.run(test_variance())
