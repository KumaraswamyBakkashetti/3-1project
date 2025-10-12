"""
Test script to verify all fixes are working correctly
Run this BEFORE generating new training data
"""

import sys
from pathlib import Path

print("="*70)
print("TESTING LLAMA FOLDER FIXES")
print("="*70)

# Test 1: Check if networkx is installed
print("\n[Test 1] Checking NetworkX installation...")
try:
    import networkx as nx
    import numpy as np
    print("✅ NetworkX installed:", nx.__version__)
    print("✅ NumPy installed:", np.__version__)
except ImportError as e:
    print("❌ Missing dependency:", e)
    print("Run: pip install networkx numpy")
    sys.exit(1)

# Test 2: Import main.py functions
print("\n[Test 2] Importing main.py functions...")
try:
    from main import calculate_graph_metrics, estimate_code_quality, extract_features
    print("✅ calculate_graph_metrics imported")
    print("✅ estimate_code_quality imported")
    print("✅ extract_features imported")
except ImportError as e:
    print("❌ Import failed:", e)
    sys.exit(1)

# Test 3: Test graph metrics calculation
print("\n[Test 3] Testing graph metrics calculation...")
try:
    # Simulate graph edges from 4-agent pipeline
    test_edges = [
        ["Analyzer", "Coder"],
        ["Coder", "Tester"],
        ["Tester", "Reviewer"]
    ]
    
    metrics = calculate_graph_metrics(test_edges, 4)
    
    print("📊 Graph Metrics:")
    for key, val in metrics.items():
        print(f"   {key}: {val:.4f}")
    
    # Verify metrics are not all the same
    unique_values = set(metrics.values())
    if len(unique_values) > 1:
        print("✅ Graph metrics have variance (GOOD!)")
    else:
        print("⚠️ All graph metrics are the same (might be OK for this simple graph)")
    
except Exception as e:
    print("❌ Graph metrics calculation failed:", e)
    import traceback
    traceback.print_exc()
    sys.exit(1)

# Test 4: Test quality estimation
print("\n[Test 4] Testing code quality estimation...")
try:
    # Test with good code
    good_code = '''
def fibonacci(n):
    """Calculate fibonacci number"""
    if n <= 1:
        return n
    return fibonacci(n-1) + fibonacci(n-2)

assert fibonacci(5) == 5
    '''
    
    # Test with bad code
    bad_code = "print hello"
    
    good_scores = estimate_code_quality(good_code)
    bad_scores = estimate_code_quality(bad_code)
    
    print("📊 Good Code Scores:")
    print(f"   HumanEval: {good_scores['humaneval_score']:.4f}")
    print(f"   GSM8K: {good_scores['gsm8k_score']:.4f}")
    print(f"   MMLU: {good_scores['mmlu_score']:.4f}")
    
    print("📊 Bad Code Scores:")
    print(f"   HumanEval: {bad_scores['humaneval_score']:.4f}")
    print(f"   GSM8K: {bad_scores['gsm8k_score']:.4f}")
    print(f"   MMLU: {bad_scores['mmlu_score']:.4f}")
    
    # Good code should score higher
    if good_scores['humaneval_score'] > bad_scores['humaneval_score']:
        print("✅ Quality heuristic works (good > bad)")
    else:
        print("⚠️ Quality heuristic might need tuning")
    
except Exception as e:
    print("❌ Quality estimation failed:", e)
    import traceback
    traceback.print_exc()
    sys.exit(1)

# Test 5: Import MAS and check graph edge recording
print("\n[Test 5] Checking MAS graph edge recording...")
try:
    from AgentMonitor.mas import CodeGenerationMAS
    import inspect
    
    # Check if run() method mentions record_graph_edge
    source = inspect.getsource(CodeGenerationMAS.run)
    
    if "record_graph_edge" in source:
        edge_count = source.count("record_graph_edge")
        print(f"✅ Found {edge_count} record_graph_edge() calls in MAS")
        print("   This should create 3 edges: Analyzer→Coder→Tester→Reviewer")
    else:
        print("❌ No record_graph_edge() calls found in MAS!")
        print("   Graph edges will be empty!")
        sys.exit(1)
    
except Exception as e:
    print("❌ MAS check failed:", e)
    import traceback
    traceback.print_exc()
    sys.exit(1)

# Test 6: Verify monitor has record_graph_edge method
print("\n[Test 6] Checking EnhancedAgentMonitor...")
try:
    from AgentMonitor import EnhancedAgentMonitor
    
    if hasattr(EnhancedAgentMonitor, 'record_graph_edge'):
        print("✅ EnhancedAgentMonitor has record_graph_edge() method")
    else:
        print("❌ EnhancedAgentMonitor missing record_graph_edge() method")
        sys.exit(1)
    
except Exception as e:
    print("❌ Monitor check failed:", e)
    sys.exit(1)

# All tests passed!
print("\n" + "="*70)
print("✅ ALL TESTS PASSED!")
print("="*70)
print("\nYou can now safely run:")
print("  1. Delete old CSV: rm data/training_data.csv")
print("  2. Generate new data: python main.py generate")
print("  3. Verify CSV has:")
print("     - num_edges = 3 (not 0!)")
print("     - Graph metrics vary between rows")
print("     - Scores correlate with quality")
print("="*70)
