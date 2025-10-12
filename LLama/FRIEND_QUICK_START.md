# 👋 Hi! Quick Start Guide for Data Generation

**From**: Your friend who needs training data  
**Task**: Run code 50+ times to generate training dataset  
**Time**: ~1 hour per run, so spread over a few days  
**Don't worry**: You don't need to understand the code!

---

## 🚀 Step 1: Setup (One-Time, 5 minutes)

### 1.1 Get the Code
You should have received a folder called `Final/`. Put it somewhere on your computer.

### 1.2 Install Python
- Download Python 3.8+ from https://python.org
- **Important**: Check "Add Python to PATH" during installation

### 1.3 Create Virtual Environment
Open terminal/command prompt in the `Final/` folder:

```bash
# Windows (PowerShell or CMD):
python -m venv venv
venv\Scripts\activate

# Mac/Linux:
python3 -m venv venv
source venv/bin/activate
```

You'll see `(venv)` in your terminal. Good!

### 1.4 Install Dependencies
```bash
pip install -r requirements.txt
```

This takes ~5 minutes. Get coffee ☕

### 1.5 Add Your API Key

**CRITICAL**: Open the `.env` file and change the API key:

```bash
# Before (DON'T USE THIS):
GEMINI_API_KEY=some_old_key

# After (USE YOUR KEY):
GEMINI_API_KEY=your_actual_api_key_here
```

**Where to get API key**:
- Google Gemini: https://makersuite.google.com/app/apikey
- OR ask your friend if using different LLM

---

## 🎯 Step 2: Generate Data (Run 50+ Times)

### The One Command You Need:
```bash
python main.py generate
```

**That's it!** Just run this command 50+ times.

### What Happens:
```
Running Task 1/5: Write a function to calculate factorial
[MONITORING] Initializing...
[AGENT] Analyzer analyzing task...
[AGENT] Coder generating code...
[AGENT] Tester testing code...
[AGENT] Reviewer reviewing result...
[EXTRACTING] 16 features...
[EVALUATING] On benchmarks... (this is slow, ~30 min)
✅ Generated 1 sample
💾 Saved: data/training_data.csv
```

**Each run takes**: ~1 hour (because of benchmark evaluation)  
**You need**: 50+ runs  
**Total time**: 50+ hours (spread over days/weeks)

---

## 📊 Step 3: Track Progress

### Check How Many Samples You've Generated:
```bash
# Windows PowerShell:
(Get-Content data\training_data.csv | Measure-Object -Line).Lines - 1

# Mac/Linux:
wc -l < data/training_data.csv
```

**Output**: Number of samples (should be 50+)

### View the Data:
```bash
# Windows:
notepad data\training_data.csv

# Mac/Linux:
cat data/training_data.csv
```

You'll see a CSV with 20 columns (16 features + 4 scores).

---

## ⚡ Pro Tips

### Run in Background
Don't want to keep terminal open?

**Windows**:
```powershell
Start-Process python -ArgumentList "main.py","generate" -WindowStyle Hidden
```

**Mac/Linux**:
```bash
nohup python main.py generate > output.log 2>&1 &
```

### Run Multiple Times Automatically
Create a simple loop:

**Windows** (`generate_50.bat`):
```batch
@echo off
for /L %%i in (1,1,50) do (
    echo Running iteration %%i of 50
    python main.py generate
    echo Completed %%i samples
)
echo All done! Send data/training_data.csv to your friend.
pause
```

**Mac/Linux** (`generate_50.sh`):
```bash
#!/bin/bash
for i in {1..50}; do
    echo "Running iteration $i of 50"
    python main.py generate
    echo "Completed $i samples"
done
echo "All done! Send data/training_data.csv to your friend."
```

Run it:
```bash
# Windows:
generate_50.bat

# Mac/Linux:
chmod +x generate_50.sh
./generate_50.sh
```

### Schedule Overnight
Run while you sleep!

**Windows Task Scheduler**:
1. Open Task Scheduler
2. Create Basic Task
3. Set trigger (e.g., every night at 11 PM)
4. Action: Start Program → `python.exe`
5. Arguments: `main.py generate`
6. Start in: `C:\path\to\Final\`

**Mac/Linux Cron**:
```bash
# Run every night at 11 PM
0 23 * * * cd /path/to/Final && /path/to/venv/bin/python main.py generate
```

---

## 🎁 Step 4: Send to Your Friend

### After 50+ Runs:
1. Check you have 50+ samples:
   ```bash
   python -c "import pandas as pd; print(f'{len(pd.read_csv(\"data/training_data.csv\"))} samples')"
   ```

2. Send **ONLY** this file:
   ```
   data/training_data.csv
   ```

3. Email/upload to your friend

**That's it!** Your job is done! 🎉

---

## 🐛 Troubleshooting

### "Module not found" error
```bash
# Make sure venv is activated (you should see "(venv)" in terminal)
venv\Scripts\activate  # Windows
source venv/bin/activate  # Mac/Linux

# Reinstall dependencies
pip install -r requirements.txt
```

### "API key invalid" error
```bash
# Check .env file
# Make sure GEMINI_API_KEY=your_actual_key (no spaces, no quotes)
```

### "Permission denied" error
```bash
# Run as administrator (Windows) or use sudo (Mac/Linux)
```

### Code crashes / errors
```bash
# Check if you have internet connection (needed for LLM API)
# Check API key is valid
# Check Python version: python --version (should be 3.8+)
```

### Takes too long (>2 hours per run)
```bash
# Normal! Benchmark evaluation is slow
# Consider running overnight or in background
```

### Want to verify it's working
```bash
# Check the CSV file grows after each run
# Look at data/training_data.csv
# Each row = 1 sample
```

---

## 📞 Need Help?

### Quick Checks:
1. ✅ Virtual environment activated? (see `(venv)` in terminal)
2. ✅ API key in `.env` file?
3. ✅ Dependencies installed? (`pip list` shows pandas, xgboost, etc.)
4. ✅ Internet connection?
5. ✅ Python 3.8+? (`python --version`)

### Still Stuck?
Contact your friend who sent you this code!

---

## 🎯 Summary (TL;DR)

```bash
# ONE-TIME SETUP (5 minutes):
python -m venv venv
venv\Scripts\activate          # Windows
pip install -r requirements.txt
# Edit .env with your API key

# REPEAT 50+ TIMES (~1 hour each):
python main.py generate

# WHEN DONE (after 50+ runs):
# Send: data/training_data.csv to your friend
```

**That's literally it!** Simple, right? 😊

---

## 📈 Expected Output

### After 1 Run:
```csv
avg_personal_score,min_personal_score,...,label_mas_score
0.65,0.45,...,0.523
```

### After 50 Runs:
```csv
avg_personal_score,min_personal_score,...,label_mas_score
0.65,0.45,...,0.523
0.72,0.58,...,0.612
0.48,0.32,...,0.387
... (47 more rows)
```

### Each Row = One MAS Execution:
- 16 feature columns (metrics about how MAS performed)
- 4 score columns (benchmark results)
- 20 columns total

---

## 🏆 You're Helping Research!

**What you're doing**:
- Running a Multi-Agent System (MAS) on coding tasks
- Collecting performance data (features + benchmark scores)
- Your data will train an ML model to predict MAS performance

**Why it matters**:
- Evaluating MAS on benchmarks takes HOURS
- With your data, we can predict performance in SECONDS
- This makes MAS development 100x faster!

**Thank you!** 🙏

---

## 🎬 Walkthrough Example

```bash
# Open terminal in Final/ folder
cd C:\Users\YourName\Desktop\Final

# Activate virtual environment
venv\Scripts\activate
# You see: (venv) C:\Users\YourName\Desktop\Final>

# Run generation (1st time)
python main.py generate
# Wait ~1 hour...
# Output: ✅ Generated 1 samples

# Check progress
python -c "import pandas as pd; print(len(pd.read_csv('data/training_data.csv')))"
# Output: 1

# Run again (2nd time)
python main.py generate
# Wait ~1 hour...
# Output: ✅ Generated 2 samples

# Check progress
python -c "import pandas as pd; print(len(pd.read_csv('data/training_data.csv')))"
# Output: 2

# ... repeat until 50+

# Check final count
python -c "import pandas as pd; print(len(pd.read_csv('data/training_data.csv')))"
# Output: 53

# Send file to friend
# Email: data/training_data.csv
```

**Done!** 🎉

---

## ⏰ Time Estimates

| Task | Time | Frequency |
|------|------|-----------|
| Setup | 5 min | Once |
| Single run | 1 hour | 50+ times |
| Check progress | 10 sec | Anytime |
| Send data | 1 min | Once at end |
| **Total** | **~50 hours** | **Over days/weeks** |

**Tip**: Run overnight, during work, or in background!

---

## 🎁 Bonus: Advanced Options

### Use Different Tasks
Edit `main.py` line 344 to add more varied tasks:

```python
tasks = [
    "Write a function to calculate factorial",
    "Create a binary search function",
    # Add your own:
    "Implement quicksort algorithm",
    "Write a function to detect palindromes",
    # More variety = better training data!
]
```

### Check Data Quality
```python
import pandas as pd
df = pd.read_csv('data/training_data.csv')
print(df.describe())  # Statistics
print(df.head())      # First 5 rows
print(df.isnull().sum())  # Missing values
```

### Visualize Progress
```python
import pandas as pd
import matplotlib.pyplot as plt

df = pd.read_csv('data/training_data.csv')
df['label_mas_score'].hist(bins=20)
plt.xlabel('MAS Score')
plt.ylabel('Frequency')
plt.title(f'Distribution of {len(df)} Samples')
plt.show()
```

But honestly, **you don't need this**. Just run the command 50+ times! 😊

---

**Good luck! And thank you for helping with this research!** 🚀
