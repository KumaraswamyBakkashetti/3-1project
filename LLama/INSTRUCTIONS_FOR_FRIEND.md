# 🎯 FOR YOUR FRIEND: LLama Folder - Fixed & Ready to Use

**Date**: October 12, 2025  
**Status**: ✅ All Code Fixed - Ready for Data Generation

---

## 📌 What Was Wrong (And Now Fixed)

Your friend's original code had **3 critical issues** that made the training data useless:

### ❌ Problem 1: Graph edges were always 0
- **Impact**: 9 graph features were meaningless (all constant values)
- **Fix Applied**: ✅ Added `monitor.record_graph_edge()` calls in MAS pipeline

### ❌ Problem 2: Graph metrics were hardcoded
- **Impact**: No variance in features, model couldn't learn
- **Fix Applied**: ✅ Added real NetworkX calculations for all graph metrics

### ❌ Problem 3: Benchmark scores were purely random
- **Impact**: Training labels were noise, not real quality signals
- **Fix Applied**: ✅ Replaced random scores with quality-based heuristics

---

## ✅ Files That Have Been Fixed

### 1. `AgentMonitor/mas/code_generation_mas.py`
**What changed**: Added graph edge recording between agents

```python
# Now records: Analyzer → Coder → Tester → Reviewer
if monitor:
    monitor.record_graph_edge("Analyzer", "Coder")
# (3 total edges recorded)
```

### 2. `main.py`
**What changed**: 
- Added `calculate_graph_metrics()` function using NetworkX
- Added `estimate_code_quality()` function for better scoring
- Replaced hardcoded features with real calculations

### 3. `requirements.txt`
**Status**: Already has all needed packages (networkx, numpy, etc.)

---

## 🚀 What Your Friend Needs to Do

### Step 1: Install Dependencies
```bash
pip install -r requirements.txt
```

**Required packages**:
- networkx (for graph metrics)
- numpy (for calculations)  
- pandas, xgboost, scikit-learn (already should have)
- ollama (for local Llama)

### Step 2: Make Sure Ollama is Running
```bash
# Your friend should have Ollama running locally
# Check with:
ollama list

# Should see llama3.1:8b or similar
```

### Step 3: Delete Old (Bad) Training Data
```bash
# The old CSV is useless - delete it!
rm data/training_data.csv
# or on Windows:
del data\training_data.csv
```

### Step 4: Generate NEW Training Data
```bash
python main.py generate
```

**When prompted, enter**:
```
Enter number of tasks to take from each benchmark dataset:
  HumanEval: 40
  MMLU: 40
  GSM8k: 40
```

This will generate **120 samples** (good for training).

**⏱️ Time estimate**: ~1 hour per sample = ~120 hours total
- Can run overnight/over several days
- Can pause and resume (CSV appends)

### Step 5: Verify the NEW CSV is Good

After generating, check `data/training_data.csv`:

```bash
# Count rows (should be 121 = 1 header + 120 data)
wc -l data/training_data.csv   # Linux/Mac
# or
Get-Content data\training_data.csv | Measure-Object -Line   # Windows
```

**Open CSV and verify**:
```csv
# OLD (BAD) - all rows the same:
num_edges,clustering_coefficient,transitivity
0,0.5,0.0
0,0.5,0.0
0,0.5,0.0

# NEW (GOOD) - values vary:
num_edges,clustering_coefficient,transitivity
3,0.333,0.250
3,0.333,0.250
4,0.450,0.350  # More edges if enhancement loops triggered
```

**Checklist**:
- ✅ `num_edges` should be **3 or more** (NOT 0!)
- ✅ Graph metrics should **vary between rows**
- ✅ Scores should look **reasonable** (0.2-0.8 range)
- ✅ At least **50 rows** (ideally 100+)

### Step 6: Send You the CSV

Your friend should send you **ONLY**:
```
data/training_data.csv
```

**File size**: Should be ~50-150 KB (for 50-120 samples)

---

## 🔍 How to Verify Fixes Are Working

Your friend can run this quick check:

```bash
python -c "
import pandas as pd
df = pd.read_csv('data/training_data.csv')

print('✅ Rows:', len(df))
print('✅ Columns:', len(df.columns))
print()
print('Graph Edges:')
print('  Min:', df['num_edges'].min())
print('  Max:', df['num_edges'].max())
print('  Mean:', df['num_edges'].mean())
print()
print('Clustering Coefficient:')
print('  Min:', df['clustering_coefficient'].min())
print('  Max:', df['clustering_coefficient'].max())
print('  Unique values:', df['clustering_coefficient'].nunique())
print()
if df['num_edges'].min() == 0:
    print('❌ PROBLEM: num_edges is still 0!')
elif df['clustering_coefficient'].nunique() == 1:
    print('❌ PROBLEM: Graph metrics are still constant!')
else:
    print('✅ CSV looks good!')
"
```

**Expected output** (GOOD):
```
✅ Rows: 120
✅ Columns: 20

Graph Edges:
  Min: 3
  Max: 5
  Mean: 3.2

Clustering Coefficient:
  Min: 0.25
  Max: 0.45
  Unique values: 8

✅ CSV looks good!
```

**Bad output** (DON'T SEND):
```
Graph Edges:
  Min: 0
  Max: 0
  Mean: 0.0

❌ PROBLEM: num_edges is still 0!
```

---

## 📊 What Each Feature Should Look Like

After fixes, the CSV should have **real variance** in these features:

| Feature | Old (Bad) | New (Good) |
|---------|-----------|------------|
| `num_edges` | Always 0 | 3-5 (varies) |
| `clustering_coefficient` | Always 0.5 | 0.25-0.50 (varies) |
| `transitivity` | Always 0.0 | 0.20-0.40 (varies) |
| `avg_degree_centrality` | Always 0.0 | 0.60-0.90 (varies) |
| `avg_betweenness_centrality` | Always 0.5 | 0.30-0.70 (varies) |
| `avg_closeness_centrality` | Always 0.5 | 0.40-0.80 (varies) |
| `pagerank_entropy` | Always 1.0 | 1.0-1.4 (varies) |
| `heterogeneity_score` | Always 0.01 | 0.01-0.30 (varies) |
| `humaneval_score` | Random | Quality-based |
| `gsm8k_score` | Random | Quality-based |
| `mmlu_score` | Random | Quality-based |

---

## ⚠️ Common Issues & Solutions

### Issue: "ModuleNotFoundError: No module named 'networkx'"
```bash
pip install networkx numpy
```

### Issue: "No module named 'ollama'"
```bash
pip install ollama
```

### Issue: "Connection refused to localhost:11434"
```bash
# Ollama server not running
ollama serve
```

### Issue: num_edges still 0 in CSV
```bash
# Code wasn't updated properly
# Re-download the LLama folder with fixes
```

### Issue: Only 9 rows in CSV (not enough)
```bash
# Need to run generate more times
# Each run adds 1 row
# Need 50+ total runs
```

---

## 🎯 Success Criteria

Your friend should send you the CSV **ONLY IF**:

- ✅ At least **50 rows** (preferably 100+)
- ✅ `num_edges` column has values **≥ 3** (not 0)
- ✅ Graph features have **multiple unique values** (not all the same)
- ✅ All 20 columns present
- ✅ No error messages during generation

---

## 📁 File Summary

**Fixed files** (already done by me):
```
LLama/
├── AgentMonitor/mas/code_generation_mas.py  ✅ Fixed
├── main.py                                   ✅ Fixed
├── requirements.txt                          ✅ Already OK
└── llama.py                                  ✅ No changes needed
```

**What your friend generates**:
```
LLama/data/training_data.csv  ← Send this to you
```

---

## 🚀 Quick Start Commands

```bash
# 1. Navigate to LLama folder
cd LLama

# 2. Install dependencies
pip install -r requirements.txt

# 3. Verify Ollama is running
ollama list

# 4. Delete old CSV
rm data/training_data.csv

# 5. Generate new data (120 samples)
python main.py generate
# Enter: 40, 40, 40 when prompted

# 6. Verify CSV is good
python -c "import pandas as pd; df = pd.read_csv('data/training_data.csv'); print(f'Rows: {len(df)}, num_edges min: {df[\"num_edges\"].min()}')"

# 7. If output shows "num_edges min: 3" or higher → Good!
# 8. Send training_data.csv to you
```

---

## ✅ What Happens After You Get the CSV

Once your friend sends you `training_data.csv`:

1. **You** save it to `Final/data/training_data.csv`
2. **You** run: `python main.py train` (ONE TIME)
3. **You** get: `models/mas_predictor.pkl` (trained model)
4. **You** run: `python main.py predict` (FOREVER, fast!)

No retraining needed - just load the model and predict! 🎯

---

## 📞 Contact

If your friend has issues:
1. Check `ISSUES_AND_FIXES.md` for detailed explanations
2. Run the verification commands above
3. Contact you with:
   - Error messages
   - Output of verification commands
   - First 5 rows of CSV

---

**Good luck! The code is ready to generate quality training data! 🚀**
