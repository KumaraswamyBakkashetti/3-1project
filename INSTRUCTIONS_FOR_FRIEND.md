# Instructions for Dataset Generation

## 👋 Hi! You've been asked to generate the AgentMonitor training dataset.

This document provides **step-by-step instructions** to help you complete this task successfully.

---

## 🎯 Your Mission

Generate a CSV file with **5 rows × 20 columns** containing Multi-Agent System (MAS) evaluation data.

**What you'll do**:
1. Set up the environment
2. Run the evaluation script
3. Wait for completion (~30-45 minutes)
4. Send back the generated CSV file

**What you'll get**:
- File: `data/mas_benchmark_results.csv`
- Format: 5 MAS variants tested on 3 benchmarks
- Data: 20 columns (features + benchmark scores + label)

---

## 🔧 Prerequisites

### Required Software
- **Python 3.8+** (check: `python --version`)
- **pip** (Python package manager)
- **LLM Setup**: One of the following:
  - Ollama with Llama3 (recommended, free, local)
  - Gemini API key (requires Google account)
  - OpenAI API key (costs money)

### Recommended Setup: Ollama + Llama3

```bash
# Install Ollama (if not already installed)
# Visit: https://ollama.com/download

# Pull Llama3 model
ollama pull llama3

# Verify it works
ollama run llama3 "Hello, world!"
```

---

## 📋 Step-by-Step Instructions

### Step 1: Extract the Project

```bash
# Extract the provided AgentMonitor.zip to a location like:
# C:\Users\YourName\AgentMonitor\Final
# or
# ~/AgentMonitor/Final

# Navigate to the folder
cd AgentMonitor/Final
```

### Step 2: Set Up Python Environment

```bash
# Create virtual environment (recommended)
python -m venv venv

# Activate virtual environment
# Windows PowerShell:
venv\Scripts\activate

# Windows CMD:
venv\Scripts\activate.bat

# Linux/Mac:
source venv/bin/activate

# You should see (venv) in your terminal prompt
```

### Step 3: Install Dependencies

```bash
# Install all required packages
pip install -r requirements.txt

# Wait for installation to complete
# This installs: pandas, numpy, xgboost, networkx, tqdm, etc.
```

### Step 4: Configure API Key

**Option A: Using Ollama (Recommended - Free & Local)**

If you have Ollama installed with Llama3:

1. Open `Agent_Monitor/evaluate_mas_on_benchmarks.py`
2. Find this section (around line 237):

```python
mas_variants = [
    {
        'name': 'CodeMAS_v1',
        'threshold': 0.6,
        'max_retries': 2,
        'api_key': os.getenv('GEMINI_API_KEY')  # ← CHANGE THIS
    },
    ...
]
```

3. Replace `os.getenv('GEMINI_API_KEY')` with `'ollama'` in all 5 variants:

```python
'api_key': 'ollama'
```

**Option B: Using Gemini API**

```bash
# Windows PowerShell:
$env:GEMINI_API_KEY = "your-gemini-api-key-here"

# Linux/Mac:
export GEMINI_API_KEY="your-gemini-api-key-here"
```

### Step 5: Verify Benchmark Data Exists

```bash
# Check that these files exist:
dir BenchmarkDatasetFolder\HumanEval\data.csv    # Windows
dir BenchmarkDatasetFolder\GSM8k\data.csv
dir BenchmarkDatasetFolder\MMLU\data.csv

# Or on Linux/Mac:
ls BenchmarkDatasetFolder/HumanEval/data.csv
ls BenchmarkDatasetFolder/GSM8k/data.csv
ls BenchmarkDatasetFolder/MMLU/data.csv
```

If any are missing, let the person who sent you this know!

### Step 6: Run the Evaluation Script

```bash
# Start the evaluation
python Agent_Monitor/evaluate_mas_on_benchmarks.py
```

**You'll be prompted**:

```
Run evaluation? (y/n): 
```
→ Type **`y`** and press Enter

```
Samples per benchmark (default 10, min 5, max 100):
```
→ Type **`10`** and press Enter (or `5` for faster testing)

### Step 7: Wait for Completion

The script will now:
1. Test 5 MAS variants
2. Each variant runs on 3 benchmarks (HumanEval, GSM8K, MMLU)
3. Each benchmark processes 10 samples
4. Total: **5 MAS × 3 benchmarks × 10 samples = 150 executions**

**Expected Duration**:
- With 10 samples: ~30-45 minutes
- With 5 samples: ~15-20 minutes (faster testing)

**Progress Display**:
```
============================================================
Evaluating MAS: CodeMAS_v1
Configuration: {'name': 'CodeMAS_v1', 'threshold': 0.6, ...}
============================================================

[HUMANEVAL] Evaluating CodeMAS_v1 on HumanEval...
HumanEval: 100%|██████████| 10/10 [05:23<00:00, 32.4s/it]
[HUMANEVAL] CodeMAS_v1 score: 0.7200

[GSM8K] Evaluating CodeMAS_v1 on GSM8K...
GSM8K: 100%|██████████| 10/10 [04:12<00:00, 25.2s/it]
[GSM8K] CodeMAS_v1 score: 0.5800

[MMLU] Evaluating CodeMAS_v1 on MMLU...
MMLU: 100%|██████████| 10/10 [03:45<00:00, 22.5s/it]
[MMLU] CodeMAS_v1 score: 0.6100

============================================================
Results for CodeMAS_v1:
  HumanEval: 0.7200
  GSM8K:     0.5800
  MMLU:      0.6100
  MAS Score: 0.6300
  Features collected: 30 runs
============================================================
```

### Step 8: Verify the Output

After completion, check the generated file:

```bash
# Windows:
dir data\mas_benchmark_results.csv

# Linux/Mac:
ls -lh data/mas_benchmark_results.csv
```

**Quick Verification**:

```python
python -c "import pandas as pd; df = pd.read_csv('data/mas_benchmark_results.csv'); print(f'Shape: {df.shape}'); print(f'Columns: {len(df.columns)}'); print(f'Missing values: {df.isnull().sum().sum()}')"
```

**Expected Output**:
```
Shape: (5, 20)
Columns: 20
Missing values: 0
```

### Step 9: Send the File Back

1. Locate the file: `data/mas_benchmark_results.csv`
2. **Verify it has**:
   - Exactly 5 rows (one per MAS variant)
   - Exactly 20 columns (features + scores + label)
   - No missing values
3. Send it via email/file share to the person who requested it

---

## 📊 Understanding the Output

### CSV Structure (20 columns)

The generated CSV contains:

**Columns 1-6: System Features**
- `avg_personal_score` - Average agent performance
- `min_personal_score` - Minimum agent performance
- `max_loops` - Maximum enhancement loops
- `total_latency` - Total execution time (seconds)
- `total_token_usage` - Total tokens consumed
- `num_agents_triggered_enhancement` - Agents needing enhancement

**Columns 7-15: Graph Features**
- `num_nodes` - Number of agent nodes
- `num_edges` - Number of interactions
- `clustering_coefficient` - Local clustering
- `transitivity` - Global clustering
- `avg_degree_centrality` - Average connections
- `avg_betweenness_centrality` - Average bridge importance
- `avg_closeness_centrality` - Average proximity
- `pagerank_entropy` - Information distribution
- `heterogeneity_score` - Network diversity

**Column 16: Collective Score**
- `collective_score` - Overall coordination

**Columns 17-19: Benchmark Scores**
- `humaneval_score` - Code generation accuracy
- `gsm8k_score` - Math reasoning accuracy
- `mmlu_score` - Knowledge/QA accuracy

**Column 20: Label (Target)**
- `label_mas_score` - Overall MAS score (0.5×HE + 0.3×GSM + 0.2×MM)

### Example Row

```csv
0.63,0.40,2,25.48,1384,3,5,4,0.18,0.22,0.36,0.14,0.27,2.16,0.008,0.65,0.72,0.58,0.61,0.63
```

This represents one MAS variant with:
- System performance: avg=0.63, min=0.40, 2 loops, 25.48s latency
- Graph structure: 5 nodes, 4 edges, moderate clustering
- Benchmark results: HumanEval=0.72, GSM8K=0.58, MMLU=0.61
- Overall score: 0.63

---

## 🐛 Troubleshooting

### Problem: "ModuleNotFoundError: No module named 'pandas'"

**Solution**: You forgot to install dependencies
```bash
pip install -r requirements.txt
```

### Problem: "FileNotFoundError: BenchmarkDatasetFolder/HumanEval/data.csv"

**Solution**: Benchmark data is missing. Contact the person who sent you this project.

### Problem: "API key error" or "Authentication failed"

**Solution**: 
- If using Ollama: Make sure Ollama is running (`ollama serve`)
- If using Gemini: Check your API key is set correctly
- Verify the key with: `echo $env:GEMINI_API_KEY` (Windows) or `echo $GEMINI_API_KEY` (Linux/Mac)

### Problem: Script is very slow or hanging

**Solution**: 
- Check your internet connection (if using cloud APIs)
- Reduce samples: Use 5 instead of 10
- If using Ollama, ensure Llama3 model is downloaded: `ollama pull llama3`

### Problem: "Out of memory" error

**Solution**: 
- Close other applications
- Use fewer samples (5 instead of 10)
- Restart your computer and try again

### Problem: CSV has wrong dimensions (not 5×20)

**Solution**: 
- Delete `data/mas_benchmark_results.csv`
- Run the script again from scratch
- Ensure all 5 MAS variants complete successfully

---

## ⏱️ Time Estimates

| Samples | HumanEval | GSM8K | MMLU | Total per MAS | All 5 MAS |
|---------|-----------|-------|------|---------------|-----------|
| 5       | ~3 min    | ~2 min| ~2 min| ~7 min       | ~35 min   |
| 10      | ~5 min    | ~4 min| ~4 min| ~13 min      | ~65 min   |
| 20      | ~10 min   | ~8 min| ~7 min| ~25 min      | ~125 min  |

**Recommendation**: Start with 5 samples for testing, then run with 10 for final dataset.

---

## ✅ Final Checklist

Before sending the file back, verify:

- [ ] File exists: `data/mas_benchmark_results.csv`
- [ ] Shape is correct: 5 rows × 20 columns
- [ ] No missing values (all cells filled)
- [ ] File size is reasonable (2-5 KB)
- [ ] First row is the header with column names
- [ ] Benchmark scores are in 0-1 range
- [ ] All 5 MAS variants completed successfully

**Quick verification command**:
```bash
python -c "import pandas as pd; df = pd.read_csv('data/mas_benchmark_results.csv'); print('✓ Shape:', df.shape); print('✓ Columns:', len(df.columns)); print('✓ Missing:', df.isnull().sum().sum()); print('✓ Benchmark ranges OK' if (df[['humaneval_score', 'gsm8k_score', 'mmlu_score']].min().min() >= 0 and df[['humaneval_score', 'gsm8k_score', 'mmlu_score']].max().max() <= 1) else '✗ Benchmark ranges invalid')"
```

---

## 📞 Need Help?

If you encounter issues:

1. **Check the logs**: Look in `logs/` directory for error messages
2. **Try with fewer samples**: Use 5 instead of 10
3. **Verify setup**: Re-run the installation steps
4. **Contact support**: Reach out to the person who sent you this task

---

## 🎉 Success!

When you see this message:

```
================================================================================
All MAS Variants Evaluated!
================================================================================

Sample of results:
 avg_personal_score  min_personal_score  humaneval_score  gsm8k_score  mmlu_score  label_mas_score
               0.63                0.40             0.72         0.58        0.61             0.63
               0.71                0.52             0.78         0.65        0.68             0.72
               0.55                0.35             0.62         0.51        0.54             0.55
               0.68                0.45             0.66         0.59        0.62             0.65
               0.60                0.38             0.64         0.67        0.70             0.62

Full dataset shape: (5, 20)
Columns: ['avg_personal_score', 'min_personal_score', ...]

Saved to: data\mas_benchmark_results.csv
================================================================================

✅ Complete! Now you can train XGBoost:
   python Trainer/xgb_trainer_mas.py
```

**You're done!** 🎊

Send `data/mas_benchmark_results.csv` back and celebrate! 🎉

---

## 📚 Additional Resources

- **Project README**: See `README.md` for system overview
- **Example CSV**: Check `data/mas_benchmark_results_FORMAT_GUIDE.csv`
- **Code Documentation**: Look at docstrings in Python files

---

**Thank you for your help! Your contribution is essential for training the AgentMonitor system.** 🙏
