# ✅ Data Generation Checklist

**Print this and check off as you go!**

---

## 📋 ONE-TIME SETUP

- [ ] Downloaded Python 3.8+ from python.org
- [ ] Installed Python (checked "Add to PATH")
- [ ] Got the `Final/` folder from friend
- [ ] Opened terminal in `Final/` folder
- [ ] Created venv: `python -m venv venv`
- [ ] Activated venv: `venv\Scripts\activate` (Windows) or `source venv/bin/activate` (Mac/Linux)
- [ ] Installed packages: `pip install -r requirements.txt`
- [ ] Got API key (Gemini or other LLM)
- [ ] Edited `.env` file with my API key
- [ ] Tested: `python main.py generate` (ran once successfully)

**Setup complete!** ✅ Now just repeat the generate command 50+ times.

---

## 🔄 GENERATE DATA (Do 50+ Times)

Mark each run with a checkmark:

| Run # | Date | Time Started | Completed | Notes |
|-------|------|--------------|-----------|-------|
| 1 | __ / __ | __:__ | [ ] | |
| 2 | __ / __ | __:__ | [ ] | |
| 3 | __ / __ | __:__ | [ ] | |
| 4 | __ / __ | __:__ | [ ] | |
| 5 | __ / __ | __:__ | [ ] | |
| 6 | __ / __ | __:__ | [ ] | |
| 7 | __ / __ | __:__ | [ ] | |
| 8 | __ / __ | __:__ | [ ] | |
| 9 | __ / __ | __:__ | [ ] | |
| 10 | __ / __ | __:__ | [ ] | |
| 11 | __ / __ | __:__ | [ ] | |
| 12 | __ / __ | __:__ | [ ] | |
| 13 | __ / __ | __:__ | [ ] | |
| 14 | __ / __ | __:__ | [ ] | |
| 15 | __ / __ | __:__ | [ ] | |
| 16 | __ / __ | __:__ | [ ] | |
| 17 | __ / __ | __:__ | [ ] | |
| 18 | __ / __ | __:__ | [ ] | |
| 19 | __ / __ | __:__ | [ ] | |
| 20 | __ / __ | __:__ | [ ] | |
| 21 | __ / __ | __:__ | [ ] | |
| 22 | __ / __ | __:__ | [ ] | |
| 23 | __ / __ | __:__ | [ ] | |
| 24 | __ / __ | __:__ | [ ] | |
| 25 | __ / __ | __:__ | [ ] | |
| 26 | __ / __ | __:__ | [ ] | |
| 27 | __ / __ | __:__ | [ ] | |
| 28 | __ / __ | __:__ | [ ] | |
| 29 | __ / __ | __:__ | [ ] | |
| 30 | __ / __ | __:__ | [ ] | |
| 31 | __ / __ | __:__ | [ ] | |
| 32 | __ / __ | __:__ | [ ] | |
| 33 | __ / __ | __:__ | [ ] | |
| 34 | __ / __ | __:__ | [ ] | |
| 35 | __ / __ | __:__ | [ ] | |
| 36 | __ / __ | __:__ | [ ] | |
| 37 | __ / __ | __:__ | [ ] | |
| 38 | __ / __ | __:__ | [ ] | |
| 39 | __ / __ | __:__ | [ ] | |
| 40 | __ / __ | __:__ | [ ] | |
| 41 | __ / __ | __:__ | [ ] | |
| 42 | __ / __ | __:__ | [ ] | |
| 43 | __ / __ | __:__ | [ ] | |
| 44 | __ / __ | __:__ | [ ] | |
| 45 | __ / __ | __:__ | [ ] | |
| 46 | __ / __ | __:__ | [ ] | |
| 47 | __ / __ | __:__ | [ ] | |
| 48 | __ / __ | __:__ | [ ] | |
| 49 | __ / __ | __:__ | [ ] | |
| 50 | __ / __ | __:__ | [ ] | |
| 51 | __ / __ | __:__ | [ ] | |
| 52 | __ / __ | __:__ | [ ] | |
| 53 | __ / __ | __:__ | [ ] | |
| 54 | __ / __ | __:__ | [ ] | |
| 55 | __ / __ | __:__ | [ ] | |

**Total completed**: _____ / 50+

---

## 📊 PROGRESS CHECKS

Check every 10 runs:

- [ ] After 10 runs: Verified CSV has 10 rows
- [ ] After 20 runs: Verified CSV has 20 rows
- [ ] After 30 runs: Verified CSV has 30 rows
- [ ] After 40 runs: Verified CSV has 40 rows
- [ ] After 50 runs: Verified CSV has 50+ rows ✅

**Command to check**:
```bash
python -c "import pandas as pd; print(len(pd.read_csv('data/training_data.csv')))"
```

---

## 🎁 SEND TO FRIEND

- [ ] Verified I have 50+ samples in CSV
- [ ] Located file: `data/training_data.csv`
- [ ] Emailed/uploaded file to friend
- [ ] Confirmed friend received it

**Friend's email**: ________________________________

**Date sent**: _____ / _____ / _____

---

## 🆘 TROUBLESHOOTING

If something goes wrong, check these:

- [ ] Virtual environment activated? (see `(venv)` in terminal)
- [ ] Internet connection working?
- [ ] API key correct in `.env` file?
- [ ] Python 3.8+? (`python --version`)
- [ ] All packages installed? (`pip list`)

**Common errors and fixes**:

| Error | Fix |
|-------|-----|
| "Module not found" | `pip install -r requirements.txt` |
| "API key invalid" | Check `.env` file, no spaces/quotes |
| "Permission denied" | Run as admin / use sudo |
| Takes >2 hours | Normal! Run in background |

**Friend's contact**: ________________________________

---

## 💡 PRO TIPS

- [ ] Set up automated runs (see FRIEND_QUICK_START.md)
- [ ] Run overnight while sleeping
- [ ] Run in background during work
- [ ] Use multiple computers if available
- [ ] Check progress weekly

**Goal**: 50+ samples as fast as possible (but quality over speed!)

---

## 🎯 COMMAND CHEAT SHEET

```bash
# Activate venv (always do this first!)
venv\Scripts\activate  # Windows
source venv/bin/activate  # Mac/Linux

# Generate data (main command)
python main.py generate

# Check sample count
python -c "import pandas as pd; print(len(pd.read_csv('data/training_data.csv')))"

# View CSV
notepad data\training_data.csv  # Windows
cat data/training_data.csv  # Mac/Linux
```

---

**Print this checklist and stick it on your wall!** 📋✨

**Estimated time**: 50+ hours over 1-2 weeks  
**Your contribution**: Invaluable for research! 🙏
