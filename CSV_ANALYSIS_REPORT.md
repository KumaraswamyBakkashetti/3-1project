# 🔍 CSV Analysis Report - Why Columns Have Repeated Values

## 📊 Data Summary
- **Total rows**: 23
- **Total columns**: 19
- **Columns with constant values**: 14
- **Columns with varying values**: 5

---

## ✅ NORMAL Repeated Values (Don't Need Fixing)

### **1. Graph Structure Metrics** (Expected to be constant)

These values are **identical** because you're running the **same pipeline structure** every time:

| Column | Value(s) | Why Constant |
|--------|----------|--------------|
| `num_nodes` | 5 (87%) or 3 (13%) | Code pipeline has 5 agents, QA has 3 |
| `num_edges` | 4 (87%) or 2 (13%) | Linear pipeline: Agent1→Agent2→Agent3... |
| `clustering_coefficient` | 0.0 (100%) | No loops in linear pipeline |
| `transitivity` | 0 (100%) | No triangles in graph structure |
| `avg_betweenness_centrality` | 0.167 (100%) | Same for all linear pipelines |

**These metrics only vary if you change the pipeline structure** (e.g., parallel agents, conditional flows, feedback loops).

### **2. Benchmark Scores** (Binary evaluation)

| Column | Values | Why |
|--------|--------|-----|
| `humaneval_score` | 1.0 (78%) or 0.0 (22%) | Code either works or doesn't |
| `gsm8k_score` | 0.0 (100%) | No GSM8K tasks run yet |
| `mmlu_score` | 0.0 (100%) | No MMLU tasks run yet |

**This is normal** - you only ran HumanEval benchmarks (code generation), so GSM8K and MMLU are 0.

---

## ⚠️ PROBLEMATIC Repeated Values (Need Fixing)

### **Problem 1: `collective_score` Always 0.5** 🔴

**Impact**: Critical - This is your target variable for ML!

| Column | Value | Frequency |
|--------|-------|-----------|
| `collective_score` | 0.5 | 100% |

**Root Cause**:
```python
# In feature_aggregator.py line ~110
def get_collective_score_with_llm(agent_logs, llm_client=None):
    if not llm_client:
        return 0.5  # ← Always returning default!
```

The LLM client isn't being passed, so it **always defaults to 0.5**.

**Fix**: Ensure `llm_client` is passed from `run_with_monitor.py`

---

### **Problem 2: `min_personal_score` Always 0.0** 🟡

**Impact**: Moderate - Limits ML model learning

| Column | Value | Frequency |
|--------|-------|-----------|
| `min_personal_score` | 0.0 | 100% |

**Root Cause**: At least one agent (usually CodeExecutor or CodeReviewer) always scores 0.0.

**Why**:
- CodeExecutor skips scoring (returns None → 0.0)
- CodeReviewer often produces short text that scores low
- UnitTestWriter fails frequently

**Fix**: Improve scoring for these agents or exclude them from `min_personal_score` calculation.

---

### **Problem 3: `max_loops` Always 2** 🟡

**Impact**: Moderate - Indicates enhancement isn't working well

| Column | Value | Frequency |
|--------|-------|-----------|
| `max_loops` | 2 | 100% |

**Root Cause**: **Every agent hits maximum retries** because:
- Initial scores are below threshold (0.8)
- Enhancement doesn't improve scores enough
- System wastes time on 2 retries every time

**Evidence**:
- `avg_personal_score` ranges 0.0-0.59 (always < 0.8 threshold)
- All 23 runs hit max retries

**Fix**: Lower threshold to 0.6 or increase max_retries

---

## 📈 What IS Varying (Good!)

These columns show diversity - good for ML:

| Column | Unique Values | Range | Mean |
|--------|---------------|-------|------|
| `avg_personal_score` | 8 | 0.0 - 0.59 | 0.11 |
| `total_latency` | 23 | 8.0s - 28.1s | 12.9s |
| `total_token_usage` | 22 | 48 - 2148 | 531 |
| `num_agents_triggered_enhancement` | 4 | 1 - 4 | 3.5 |

---

## 🎯 Root Causes Summary

### **Why Graph Metrics Don't Vary**:
```
Code Pipeline (87% of runs):
RequirementAnalyzer → CodeGenerator → CodeReviewer → UnitTestWriter → CodeExecutor
(5 nodes, 4 edges, linear structure)

QA Pipeline (13% of runs):
RequirementAnalyzer → QAAnswerer → QAReviewer
(3 nodes, 2 edges, linear structure)
```

**Result**: Same structure → Same graph metrics

### **Why Collective Score Is Always 0.5**:
```python
# Current flow:
run_with_monitor.py:
  → llm_client created ✓
  → features = collect_run_features(run_state, agent_logs, llm_client)
  
feature_aggregator.py:
  → def collect_run_features(..., llm_client=None):  ← llm_client NOT passed!
  → collective_score = get_collective_score_with_llm(agent_logs, llm_client)
  → llm_client is None → return 0.5 ✗
```

### **Why Max Loops Is Always 2**:
```python
# Every agent:
initial_score: 0.0 - 0.59 (always < 0.8 threshold)
loop 1: enhance → still < 0.8
loop 2: enhance → still < 0.8
max_retries reached → stop at 2 loops
```

---

## 🔧 Fixes Needed

### **Fix 1: Collective Score** (Critical)

**File**: `Agent_Monitor/run_with_monitor.py`

**Current** (line ~95):
```python
run_state = {"agent_features": agent_features, "graph_edges": pipeline_edges, "prompt": prompt}
features = collect_run_features(run_state, agent_logs=agent_logs, llm_client=llm_client)
```

**Issue**: Check if this is actually passing llm_client correctly.

**File**: `Agent_Monitor/feature_aggregator.py`

**Current** (line ~100):
```python
def collect_run_features(run_state: Dict[str, Any], agent_logs: Optional[List[Dict[str, Any]]] = None, llm_client=None) -> Dict[str, Any]:
```

**Verify**: `llm_client` parameter is being received.

---

### **Fix 2: Lower Threshold** (Recommended)

**File**: `Agent_Monitor/agent_monitor.py` (line 32)

**Change**:
```python
# Before:
def __init__(self, api_key: Optional[str] = None, threshold: float = 0.8, max_retries: int = 2, log_dir: str = "logs"):

# After:
def __init__(self, api_key: Optional[str] = None, threshold: float = 0.6, max_retries: int = 2, log_dir: str = "logs"):
```

**Why**: Current scores range 0.0-0.59, so 0.8 is unrealistic.

---

### **Fix 3: Add Pipeline Variety** (Optional)

Create different agent combinations:

```python
# Example variations:
- Skip CodeReviewer for simple tasks
- Add PerformanceOptimizer for complex code
- Use different QA agent combinations
- Create feedback loops
```

This will create variety in graph metrics.

---

## 📊 Expected Results After Fixes

### **Before Fixes**:
```csv
collective_score: 0.5, 0.5, 0.5, 0.5, ... (useless for ML)
max_loops: 2, 2, 2, 2, ... (always max)
min_personal_score: 0.0, 0.0, 0.0, ... (always min)
```

### **After Fixes**:
```csv
collective_score: 0.3, 0.7, 0.5, 0.8, ... (varies!)
max_loops: 0, 1, 2, 0, 1, ... (varies based on quality)
min_personal_score: 0.2, 0.0, 0.5, 0.3, ... (some variation)
```

---

## 🎓 Why This Matters for ML

### **Bad for Training** ❌:
- Constant features provide **no information** to ML model
- `collective_score = 0.5` means model can't learn anything
- Model will just predict 0.5 for everything

### **Good for Training** ✅:
After fixes:
- Varying `collective_score` → Model learns patterns
- Varying `max_loops` → Model learns when enhancement helps
- System-level features already vary (latency, tokens, scores)

---

## 🚀 Action Plan

1. **Fix collective_score** (most critical)
   ```bash
   # Verify llm_client is being passed
   # Check feature_aggregator.py line 100-110
   ```

2. **Lower threshold** (quick win)
   ```bash
   # Change 0.8 → 0.6 in agent_monitor.py
   ```

3. **Re-run data generation**
   ```bash
   python safe_data_generation.py
   ```

4. **Verify variety**
   ```bash
   python analyze_csv.py
   # Should show collective_score varying now
   ```

5. **Train model**
   ```bash
   python Trainer/xgb_trainer.py
   # With varying collective_score, model will learn!
   ```

---

## 📝 Summary

**Normal Repeated Values** (13 columns):
- ✅ Graph metrics (same pipeline structure)
- ✅ Benchmark scores (binary evaluation)

**Problematic Repeated Values** (3 columns):
- 🔴 `collective_score` = 0.5 (LLM not being called)
- 🟡 `max_loops` = 2 (threshold too high)
- 🟡 `min_personal_score` = 0.0 (some agents always fail)

**Fix Priority**:
1. collective_score (blocks ML training)
2. threshold adjustment (improves efficiency)
3. min_personal_score (nice to have)

Your ML model **cannot learn** with `collective_score` always at 0.5!
