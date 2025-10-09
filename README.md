# AgentMonitor: Multi-Agent System Performance Prediction# 🤖 AgentMonitor - Multi-Agent System Monitoring Framework



## 🎯 Overview**A Python framework for monitoring, scoring, and optimizing Multi-Agent Systems (MAS) using LLM-based evaluation and XGBoost predictions.**



**AgentMonitor** is a machine learning system that predicts Multi-Agent System (MAS) performance using XGBoost regression. It monitors MAS execution, extracts behavioral features, and predicts overall system effectiveness based on agent interactions and collective behavior.**Status**: ✅ **FULLY FUNCTIONAL**  

**Date**: October 8, 2025  

### Key Innovation**Author**: Kumaraswamy Bakkashetti

Instead of evaluating MAS on expensive benchmark tasks, AgentMonitor predicts performance by analyzing:

- **System metrics**: Agent scores, enhancement loops, latency, token usage---

- **Graph features**: Interaction network topology (clustering, centrality, entropy)

- **Collective behavior**: Overall system coordination score## 📋 Table of Contents



### Architecture1. [Overview](#overview)

2. [System Architecture](#system-architecture)

```3. [Quick Start](#quick-start)

┌─────────────────────────────────────────────────────────────┐4. [LLM Integration (Gemini & Ollama)](#llm-integration)

│                    AgentMonitor Pipeline                     │5. [Components](#components)

├─────────────────────────────────────────────────────────────┤6. [Usage Guide](#usage-guide)

│                                                               │7. [Fixes Applied](#fixes-applied)

│  1. MAS Execution                                            │8. [Data Analysis](#data-analysis)

│     ├─ Run multi-agent pipeline (code/QA tasks)             │9. [Troubleshooting](#troubleshooting)

│     ├─ Monitor agent interactions                            │

│     └─ Log execution traces                                  │---

│                                                               │

│  2. Feature Extraction                                       │## 🎯 Overview

│     ├─ System Features (6): scores, loops, latency, tokens  │

│     ├─ Graph Features (9): topology, centrality, entropy    │AgentMonitor is an intelligent monitoring system for Multi-Agent Systems that:

│     └─ Collective Score (1): coordination measure           │

│                                                               │- **Monitors**: Tracks agent outputs with 6-dimensional scoring (factual accuracy, clarity, safety, code correctness, complexity, personal score)

│  3. Benchmark Evaluation (Training Data Generation)          │- **Enhances**: Automatically improves low-scoring outputs through iterative refinement

│     ├─ HumanEval: Code generation tasks                     │- **Collects Features**: Extracts 19 system + graph metrics (latency, tokens, loops, graph centrality, PageRank entropy)

│     ├─ GSM8K: Math reasoning tasks                          │- **Trains ML Models**: Uses XGBoost to predict collective system performance

│     ├─ MMLU: Knowledge/QA tasks                             │- **Benchmarks**: Evaluates against HumanEval (code), GSM8K (math), MMLU (knowledge)

│     └─ Weak Supervision: label = 0.5×HE + 0.3×GSM + 0.2×MM  │

│                                                               │### Key Features

│  4. XGBoost Training                                         │✅ **Dual LLM Support**: Switch between Google Gemini (cloud) and Ollama (local)  

│     ├─ Input: 16 features (15 + collective_score)           │✅ **Automated Enhancement**: Iterative improvement loop with configurable threshold  

│     ├─ Target: label_mas_score                              │✅ **Graph Analytics**: NetworkX-based pipeline topology analysis  

│     └─ Output: Trained model (xgb_model.json)               │✅ **Benchmark Integration**: HumanEval (5,893 tasks), GSM8K (6,142 problems), MMLU  

│                                                               │✅ **ML Predictions**: XGBoost regression for performance forecasting  

│  5. Prediction                                               │

│     ├─ New MAS → Extract features                           │---

│     └─ Model → Predict performance                          │

│                                                               │## 🏗️ System Architecture

└─────────────────────────────────────────────────────────────┘

```### Multi-Agent Pipelines



---**Code Generation Pipeline** (5 agents):

```

## 📁 Project StructureRequirementAnalyzer → CodeGenerator → CodeReviewer → UnitTestWriter → CodeExecutor

```

```

AgentMonitor/Final/**QA Pipeline** (3 agents):

│```

├── Agent_Monitor/                    # Core monitoring systemRequirementAnalyzer → QAAnswerer → QAReviewer

│   ├── agent_monitor.py              # MAS execution monitor```

│   ├── run_with_monitor.py           # Main entry point for MAS execution

│   ├── feature_aggregator.py         # Feature extraction from MAS runs### Monitoring Workflow

│   ├── evaluate_mas_on_benchmarks.py # Benchmark evaluation for training data

│   └── utils/```

│       ├── eval_utils.py             # Answer evaluation utilitiesUser Prompt

│       ├── graph_utils.py            # Graph metric computation    ↓

│       └── json_logger.py            # JSON logging utilitiesAgent Pipeline (MAS)

│    ↓

├── MAS/                              # Multi-Agent System pipelinesAgentMonitor (6D Scoring)

│   └── mas_pipeline.py               # Code & QA agent pipelines    ↓

│Enhancement Loop (if score < threshold)

├── Trainer/                          # Model training & prediction    ↓

│   ├── xgb_trainer_mas.py            # XGBoost training scriptFeature Aggregator (19 metrics)

│   └── predict_mas.py                # Prediction script    ↓

│XGBoost Model (Prediction)

├── BenchmarkDatasetFolder/           # Benchmark datasets    ↓

│   ├── HumanEval/CSV Logging + JSON Export

│   │   └── data.csv                  # Code generation tasks```

│   ├── GSM8k/

│   │   └── data.csv                  # Math reasoning tasks### Components Overview

│   └── MMLU/

│       └── data.csv                  # Knowledge/QA tasks| Component | File | Purpose |

│|-----------|------|---------|

├── data/                             # Generated data| **MAS Pipeline** | `MAS/mas_pipeline.py` | Multi-agent code/QA task execution |

│   ├── mas_benchmark_results.csv     # Training dataset (5×20)| **Agent Monitor** | `Agent_Monitor/agent_monitor.py` | LLM-based scoring & enhancement |

│   └── mas_benchmark_results_FORMAT_GUIDE.csv  # Example format| **Feature Aggregator** | `Agent_Monitor/feature_aggregator.py` | 19-metric feature engineering |

│| **Run Orchestrator** | `Agent_Monitor/run_with_monitor.py` | Main pipeline coordinator |

├── models/                           # Trained models| **Benchmark Runner** | `Agent_Monitor/benchmark_runner.py` | Dataset evaluation |

│   └── xgb_model.json                # XGBoost model| **XGBoost Trainer** | `Trainer/xgb_trainer.py` | ML model training |

│| **Predictor** | `Trainer/predict.py` | Performance prediction |

├── logs/                             # Execution logs

│---

├── requirements.txt                  # Python dependencies

├── README.md                         # This file## 🚀 Quick Start

└── INSTRUCTIONS_FOR_FRIEND.md        # Dataset generation guide

```### Prerequisites



---- Python 3.8+

- Virtual environment (venv)

## 🔧 Features Extracted (16 Total)- Gemini API key OR Ollama installed locally



### System Features (6)### Installation

| Feature | Description | Range |

|---------|-------------|-------|```powershell

| `avg_personal_score` | Average agent performance score | 0-1 |# 1. Clone repository

| `min_personal_score` | Minimum agent performance score | 0-1 |git clone https://github.com/KumaraswamyBakkashetti/3-1project.git

| `max_loops` | Maximum enhancement loops triggered | 0-10+ |cd Final

| `total_latency` | Total execution time (seconds) | 0-∞ |

| `total_token_usage` | Total tokens consumed | 0-∞ |# 2. Create virtual environment

| `num_agents_triggered_enhancement` | Count of agents needing enhancement | 0-N |python -m venv venv

.\venv\Scripts\Activate.ps1

### Graph Features (9)

| Feature | Description | Range |# 3. Install dependencies

|---------|-------------|-------|pip install -r requirements.txt

| `num_nodes` | Number of agent nodes | 3-10 |

| `num_edges` | Number of interactions | 2-N |# 4. Configure environment

| `clustering_coefficient` | Local clustering measure | 0-1 |# Create .env file with:

| `transitivity` | Global clustering measure | 0-1 |LLM_PROVIDER=gemini  # or "ollama"

| `avg_degree_centrality` | Average node connections | 0-1 |GEMINI_API_KEY=your_api_key_here

| `avg_betweenness_centrality` | Average bridge importance | 0-1 |GEMINI_MODEL=gemini-2.0-flash

| `avg_closeness_centrality` | Average node proximity | 0-1 |```

| `pagerank_entropy` | Information distribution | 0-∞ |

| `heterogeneity_score` | Network diversity | 0-∞ |### Basic Usage



### Collective Score (1)```powershell

| Feature | Description | Range |# Run single task

|---------|-------------|-------|python Agent_Monitor/run_with_monitor.py

| `collective_score` | Overall MAS coordination | 0-1 |# Enter: "write python code for fibonacci sequence"



### Target Labels (4) - Only in Training Data# Run benchmarks (generate training data)

| Label | Description | Formula |python Agent_Monitor/benchmark_runner.py

|-------|-------------|---------|

| `humaneval_score` | Code generation accuracy | Mean correctness |# Train XGBoost model

| `gsm8k_score` | Math reasoning accuracy | Mean correctness |python Trainer/xgb_trainer.py

| `mmlu_score` | Knowledge accuracy | Mean correctness |

| `label_mas_score` | **Prediction Target** | 0.5×HE + 0.3×GSM + 0.2×MM |# Make predictions

python Trainer/predict.py

---```



## 🚀 Installation---



### Prerequisites## 🦙 LLM Integration (Gemini & Ollama)

- Python 3.8+

- Virtual environment (recommended)### Current Status: Gemini (Cloud API)

- LLM API (Gemini, OpenAI, or Ollama with Llama3)

**Active Configuration**:

### Setup- Provider: Google Gemini 2.0 Flash

- API Key: Configured in `.env`

```bash- Model: `gemini-2.0-flash`

# Clone repository

git clone <repository-url>### Switching to Ollama (Local)

cd AgentMonitor/Final

**Why Ollama?**

# Create virtual environment- ✅ **Free**: No API costs

python -m venv venv- ✅ **Private**: Data stays local

- ✅ **Offline**: Works without internet

# Activate virtual environment- ✅ **Fast**: Local inference on GPU/CPU

# Windows:

venv\Scripts\activate**Step-by-Step Integration**:

# Linux/Mac:

source venv/bin/activate#### 1. Create LLM Wrapper

Create `Agent_Monitor/llm_wrapper.py`:

# Install dependencies```python

pip install -r requirements.txtimport os

import ollama

# Set up environment variablesimport google.generativeai as genai

# Windows PowerShell:

$env:GEMINI_API_KEY = "your-api-key-here"class OllamaClientWrapper:

    def __init__(self, model_name="llama3"):

# Linux/Mac:        self.model_name = model_name

export GEMINI_API_KEY="your-api-key-here"    

```    def generate_content(self, prompt: str) -> str:

        response = ollama.generate(model=self.model_name, prompt=prompt)

---        return response['response']



## 💡 Usageclass GeminiClientWrapper:

    def __init__(self, api_key: str, model_name="gemini-2.0-flash"):

### 1. Generate Training Dataset        genai.configure(api_key=api_key)

        self.model_name = model_name

```bash    

python Agent_Monitor/evaluate_mas_on_benchmarks.py    def generate_content(self, prompt: str) -> str:

```        model = genai.GenerativeModel(self.model_name)

        return model.generate_content(prompt).text

**Output**: `data/mas_benchmark_results.csv` (5 rows × 20 columns)

def create_llm_client(provider=None, **kwargs):

- Tests 5 MAS variants on 3 benchmarks    provider = provider or os.getenv("LLM_PROVIDER", "ollama")

- Each MAS runs 30 times (10 samples × 3 benchmarks)    if provider == "ollama":

- Features aggregated across all runs        return OllamaClientWrapper(kwargs.get("model_name", "llama3"))

- Takes ~30-45 minutes for 10 samples    elif provider == "gemini":

        return GeminiClientWrapper(kwargs.get("api_key"), kwargs.get("model_name"))

### 2. Train XGBoost Model```



```bash#### 2. Update agent_monitor.py

python Trainer/xgb_trainer_mas.py```python

```# Replace imports

from Agent_Monitor.llm_wrapper import create_llm_client

**Output**: `models/xgb_model.json`

# Update __init__

- Loads training data from `data/mas_benchmark_results.csv`def __init__(self, llm_client=None, threshold=0.6, ...):

- Uses 16 features (15 + collective_score) as X    self.client = llm_client

- Uses `label_mas_score` as y```

- Saves trained model

#### 3. Update run_with_monitor.py

### 3. Make Predictions```python

from Agent_Monitor.llm_wrapper import create_llm_client

```bash

python Trainer/predict_mas.pydef run_prompt(..., llm_provider=None):

```    llm_client = create_llm_client(provider=llm_provider)

    monitor = AgentMonitor(llm_client=llm_client, ...)

**Input**: New MAS features (16 values)  ```

**Output**: Predicted MAS performance score (0-1)

#### 4. Update .env

---```env

LLM_PROVIDER=ollama

## 📊 Training Data FormatOLLAMA_MODEL=llama3

OLLAMA_HOST=http://localhost:11434

### CSV Structure (20 columns)```



```csv#### 5. Install & Setup

avg_personal_score,min_personal_score,max_loops,total_latency,total_token_usage,num_agents_triggered_enhancement,num_nodes,num_edges,clustering_coefficient,transitivity,avg_degree_centrality,avg_betweenness_centrality,avg_closeness_centrality,pagerank_entropy,heterogeneity_score,collective_score,humaneval_score,gsm8k_score,mmlu_score,label_mas_score```powershell

0.63,0.40,2,25.48,1384,3,5,4,0.18,0.22,0.36,0.14,0.27,2.16,0.008,0.65,0.72,0.58,0.61,0.63# Install Ollama Python package

0.71,0.52,3,32.15,1876,5,6,5,0.22,0.28,0.42,0.18,0.31,2.45,0.011,0.73,0.78,0.65,0.68,0.72pip install ollama

...

```# Pull Llama model

ollama pull llama3

**Breakdown**:

- Columns 1-6: System features# Test

- Columns 7-15: Graph featuresollama run llama3 "Hello"

- Column 16: Collective score```

- Columns 17-19: Benchmark scores (training only)

- Column 20: Label (training target)#### 6. Run with Ollama

```powershell

---python Agent_Monitor/run_with_monitor.py

# Output: [INFO] Using Ollama with model: llama3

## 🧪 MAS Variants Tested```



The system evaluates 5 different MAS configurations:**Performance Comparison**:



| Variant | Threshold | Max Retries | Description || Metric | Gemini | Ollama (Llama3) |

|---------|-----------|-------------|-------------||--------|--------|----------------|

| CodeMAS_v1 | 0.6 | 2 | Balanced configuration || Cost | $0.0005/1K tokens | Free |

| CodeMAS_Aggressive | 0.5 | 3 | More enhancement loops || Latency | ~2-5s | ~3-10s (CPU), ~1-3s (GPU) |

| CodeMAS_Conservative | 0.7 | 1 | Fewer enhancement loops || Privacy | Cloud | Local |

| LogicMAS_v1 | 0.6 | 2 | Logic-focused tasks || Quality | Excellent | Good |

| QA_MAS_v1 | 0.6 | 2 | Question-answering tasks |

---

---

## 📦 Components

## 🔬 How It Works

### 1. MAS Pipeline (`MAS/mas_pipeline.py`)

### Step 1: MAS Execution with Monitoring

**Code Pipeline**:

```python- `RequirementAnalyzer`: Extracts requirements, identifies language

from Agent_Monitor.run_with_monitor import run_prompt- `CodeGenerator`: Generates working code with LLM

- `CodeReviewer`: Detects bugs and inefficiencies

data, features, raw_log, summary = run_prompt(- `UnitTestWriter`: Creates test cases

    prompt="Write a function to reverse a string",- `CodeExecutor`: Runs syntax checks and simulates execution

    task_type='code',

    api_key=os.getenv('GEMINI_API_KEY'),**QA Pipeline**:

    threshold=0.6,- `RequirementAnalyzer`: Analyzes question

    max_retries=2- `QAAnswerer`: Generates answer

)- `QAReviewer`: Reviews answer quality



# features contains 16 metrics### 2. Agent Monitor (`Agent_Monitor/agent_monitor.py`)

print(features)

# {**6-Dimensional Scoring**:

#   'avg_personal_score': 0.75,1. **personal_score**: Overall quality (0-1)

#   'min_personal_score': 0.60,2. **factual_accuracy**: Correctness (0-1)

#   'max_loops': 2,3. **clarity**: Readability (0-1)

#   ...4. **safety**: Security/ethics (0-1)

#   'collective_score': 0.825. **code_correctness**: Syntax/logic (0-1, code only)

# }6. **complexity**: Appropriate complexity (0-1)

```

**Enhancement Loop**:

### Step 2: Feature Aggregation```python

while score < threshold and loops < max_retries:

For each MAS variant:    enhanced_output = llm.enhance(current_output, suggestions)

1. Run on 10 HumanEval tasks → collect 10 feature sets    score = llm.score(enhanced_output)

2. Run on 10 GSM8K tasks → collect 10 feature sets    loops += 1

3. Run on 10 MMLU tasks → collect 10 feature sets```

4. **Aggregate**: Average each of 15 features across all 30 runs

5. Compute benchmark scores (accuracy on each benchmark)### 3. Feature Aggregator (`Agent_Monitor/feature_aggregator.py`)

6. Compute label: `0.5 × humaneval + 0.3 × gsm8k + 0.2 × mmlu`

**19 Features Collected**:

### Step 3: XGBoost Training

**System Metrics** (8):

```python- `avg_personal_score`, `max_personal_score`, `min_personal_score`

# X: 16 features (15 + collective_score)- `total_latency_sec`, `avg_token_count`

# y: label_mas_score- `max_loops`, `avg_loops`

- `collective_score` (LLM-based system-level score)

model = xgb.XGBRegressor(

    n_estimators=100,**Graph Metrics** (11):

    max_depth=5,- `num_nodes`, `num_edges`, `avg_degree`

    learning_rate=0.1- `clustering_coefficient`, `transitivity`

)- `avg_betweenness_centrality`, `avg_closeness_centrality`

model.fit(X, y)- `pagerank_entropy`, `authority_entropy`

```- `density`, `diameter`



### Step 4: Prediction**Benchmark Scores** (3):

- `humaneval_score` (code correctness)

```python- `gsm8k_score` (math reasoning)

# New MAS execution- `mmlu_score` (knowledge)

new_features = [0.68, 0.45, 2, 27.5, 1500, 3, 5, 4, 0.20, ...]  # 16 values

### 4. XGBoost Model (`Trainer/xgb_trainer.py`)

# Predict performance

predicted_score = model.predict([new_features])**Model Configuration**:

print(f"Predicted MAS Score: {predicted_score[0]:.4f}")```python

```XGBRegressor(

    n_estimators=100,

---    max_depth=5,

    learning_rate=0.1,

## 📈 Expected Performance    objective='reg:squarederror'

)

### Training Data```

- **Rows**: 5 MAS variants

- **R² Score**: 0.7-0.9 (on simulated data)**Training Requirements**:

- **MAE**: 0.05-0.15- Minimum 10 rows (50-100 recommended)

- 18 input features → 1 target (`collective_score`)

### Use Cases- Cross-validation: 5-fold KFold

- **Quick MAS evaluation**: Predict performance without running expensive benchmarks- Saved as `models/xgb_model.json`

- **MAS configuration tuning**: Test different thresholds/retries

- **Agent monitoring**: Track system health during execution---



---## 📖 Usage Guide



## 🛠️ Troubleshooting### Run Single Prompt



### Issue: Import Errors```powershell

```bashpython Agent_Monitor/run_with_monitor.py

# Solution```

pip install -r requirements.txt

```**Example**:

```

### Issue: API Key ErrorsEnter task: write python code for fibonacci sequence

```bash

# Solution: Set environment variableOutput:

$env:GEMINI_API_KEY = "your-key"✅ RequirementAnalyzer: Score 0.85

✅ CodeGenerator: Score 0.92  

# Or modify evaluate_mas_on_benchmarks.py to use Ollama✅ CodeReviewer: Score 0.88

```✅ UnitTestWriter: Score 0.79

✅ CodeExecutor: Syntax OK

### Issue: Benchmark Data Not Found

```bashFeatures saved to: data/features.csv

# Ensure these folders exist:Logs: logs/run_20251008_153042.json

BenchmarkDatasetFolder/HumanEval/data.csv```

BenchmarkDatasetFolder/GSM8k/data.csv

BenchmarkDatasetFolder/MMLU/data.csv### Generate Training Data

```

```powershell

### Issue: Execution Too Slowpython Agent_Monitor/benchmark_runner.py

```bash```

# Use fewer samples (5 instead of 10)

# In evaluate_mas_on_benchmarks.py, when prompted:**Options**:

Samples per benchmark: 5- Select dataset: HumanEval, GSM8K, MMLU

```- Number of samples: 10, 50, 100

- Output: Appends to `data/features.csv`

---

### Train XGBoost Model

## 📚 Key Files Explained

```powershell

### `agent_monitor.py`python Trainer/xgb_trainer.py

Monitors MAS execution, tracks agent interactions, implements enhancement loops.```



### `run_with_monitor.py`**Requirements**:

Main entry point. Executes MAS pipeline with monitoring enabled, returns features.- At least 10 rows in `data/features.csv`

- Varying `collective_score` values

### `feature_aggregator.py`

Extracts 16 features from MAS execution logs. Computes graph metrics, system metrics, and collective score.**Output**:

```

### `evaluate_mas_on_benchmarks.py`✅ Model trained with 5-fold CV

Generates training data by running MAS variants on benchmarks. Creates 20-column CSV.✅ R² Score: 0.73

✅ RMSE: 0.15

### `xgb_trainer_mas.py`✅ Saved to: models/xgb_model.json

Trains XGBoost model on 20-column CSV using first 16 columns as features.```



### `predict_mas.py`### Make Predictions

Loads trained model and makes predictions on new MAS feature vectors.

```powershell

---python Trainer/predict.py

```

## 🎓 Research Background

**Input**: 18 features (from latest run)  

This system implements a **weak supervision** approach for MAS evaluation:**Output**: Predicted `collective_score` (0-1)



1. **Problem**: Evaluating MAS on benchmarks is expensive (time, tokens, API costs)---

2. **Solution**: Train a predictor using cheap features (execution metrics)

3. **Training**: Use benchmark scores as labels (weak supervision)## 🔧 Fixes Applied

4. **Inference**: Predict performance from features alone (no benchmarks needed)

### Issue #1: Gemini API 404 Error ✅ FIXED

### Weak Supervision Formula

```**Problem**: Using deprecated model `gemini-1.5-flash`

label_mas_score = 0.5 × humaneval_score + 

                  0.3 × gsm8k_score + **Solution**: Updated to `gemini-2.0-flash`

                  0.2 × mmlu_score

```**Files Modified**:

- `Agent_Monitor/agent_monitor.py` (line 15)

Weights reflect task importance:- `Agent_Monitor/run_with_monitor.py` (line 29)

- **50%** Code generation (most important for coding MAS)

- **30%** Math reasoning (logical thinking)### Issue #2: All Scores Returning 0.0 ✅ FIXED

- **20%** General knowledge (factual accuracy)

**Problem**: Gemini wraps JSON in markdown code blocks (` ```json {...} ``` `), causing `json.loads()` to fail

---

**Solution**: Added `extract_json()` function to strip markdown

## 🤝 Contributing

**Code Added** (`agent_monitor.py`):

To extend this system:```python

def extract_json(raw_text: str) -> str:

1. **Add more features**: Modify `feature_aggregator.py`    raw_text = raw_text.strip()

2. **Add benchmarks**: Update `evaluate_mas_on_benchmarks.py`    if raw_text.startswith("```json"):

3. **Try different models**: Replace XGBoost in `xgb_trainer_mas.py`        raw_text = raw_text[7:]

4. **Tune hyperparameters**: Adjust XGBoost settings    elif raw_text.startswith("```"):

        raw_text = raw_text[3:]

---    if raw_text.endswith("```"):

        raw_text = raw_text[:-3]

## 📝 License    return raw_text.strip()

```

This project is part of research on Multi-Agent System evaluation and monitoring.

### Issue #3: collective_score Always 0.5 ✅ FIXED

---

**Problem**: LLM client not passed to `get_collective_score_with_llm()`

## 📧 Support

**Solution**: 

For questions or issues:1. Added `extract_json()` to feature_aggregator.py

1. Check `INSTRUCTIONS_FOR_FRIEND.md` for dataset generation guide2. Added debug logging to track LLM calls

2. Review logs in `logs/` directory3. Ensured `llm_client` passed from `run_with_monitor.py`

3. Verify CSV format matches `data/mas_benchmark_results_FORMAT_GUIDE.csv`

### Issue #4: max_loops Always 2 ✅ FIXED

---

**Problem**: Threshold (0.8) higher than typical scores (0.0-0.6)

## ✅ Quick Start Checklist

**Solution**: Lowered threshold from 0.8 → 0.6

- [ ] Install Python 3.8+

- [ ] Create virtual environment**Impact**: Fewer wasted enhancement loops, `max_loops` now varies

- [ ] Install dependencies: `pip install -r requirements.txt`

- [ ] Set API key: `$env:GEMINI_API_KEY = "your-key"`### Issue #5: Generated Code Has Markdown ✅ FIXED

- [ ] Generate data: `python Agent_Monitor/evaluate_mas_on_benchmarks.py`

- [ ] Train model: `python Trainer/xgb_trainer_mas.py`**Problem**: Code wrapped in ` ```python ... ``` ` causing syntax errors

- [ ] Make predictions: `python Trainer/predict_mas.py`

**Solution**: Strip markdown blocks from generated code

---

**Code Added** (`mas_pipeline.py`):

**Built with ❤️ for efficient Multi-Agent System evaluation**```python

if code.startswith("```python"):
    code = code[9:]
elif code.startswith("```"):
    code = code[3:]
if code.endswith("```"):
    code = code[:-3]
```

---

## 📊 Data Analysis

### Training Data Overview

**Current Status** (as of Oct 8, 2025):
- **Total rows**: 23
- **Features**: 19 columns
- **Source**: HumanEval benchmark runs

### Column Analysis

**Constant Columns** (Expected - Same pipeline structure):
- `num_nodes`: 5 (code) or 3 (QA)
- `num_edges`: 4 or 2
- `clustering_coefficient`: 0.0
- `transitivity`: 0
- `avg_betweenness_centrality`: 0.167

**Varying Columns** (Good):
- `avg_personal_score`: 0.0 - 0.59
- `total_latency_sec`: 29.8 - 92.1
- `avg_token_count`: 15 - 89
- `max_loops`: Now varies (0, 1, 2) after fix
- `collective_score`: Now varies (0.3 - 0.8) after fix

**Zero Columns** (No tasks run yet):
- `gsm8k_score`: 0.0 (100%)
- `mmlu_score`: 0.0 (100%)

### Recommendations

1. **Generate more data**: Need 50-100 rows for robust XGBoost model
2. **Diversify tasks**: Run GSM8K and MMLU benchmarks
3. **Vary pipeline structure**: Try parallel agents, conditional flows for graph metric diversity

---

## 🐛 Troubleshooting

### Gemini API Errors

**404 Error - Model not found**:
```
Error: models/gemini-1.5-flash is not found
Solution: Update to gemini-2.0-flash
```

**JSON Parsing Errors**:
```
Error: json.loads() failed
Solution: Use extract_json() to strip markdown
```

### Ollama Issues

**Connection refused**:
```powershell
# Check if Ollama is running
ollama list

# Start Ollama service
ollama serve
```

**Model not found**:
```powershell
# Pull model
ollama pull llama3
```

### XGBoost Training Fails

**Not enough data**:
```
Error: Need at least 10 rows
Solution: Run benchmark_runner.py to generate more data
```

**constant target variable**:
```
Error: collective_score is constant
Solution: Ensure LLM client is passed correctly (check fix #3)
```

### Enhancement Loop Issues

**All agents hit max_retries**:
```
Issue: max_loops always 2
Solution: Lower threshold (0.8 → 0.6) or increase max_retries
```

---

## 📁 Project Structure

```
Final/
├── Agent_Monitor/
│   ├── agent_monitor.py          # Core monitoring + scoring
│   ├── feature_aggregator.py     # 19-feature extraction
│   ├── run_with_monitor.py       # Main orchestrator
│   ├── benchmark_runner.py       # Dataset evaluation
│   └── utils/
│       ├── eval_utils.py         # Benchmark scoring
│       ├── graph_utils.py        # NetworkX analytics
│       └── json_logger.py        # JSON logging
├── MAS/
│   └── mas_pipeline.py           # Multi-agent pipelines
├── Trainer/
│   ├── xgb_trainer.py            # XGBoost training
│   └── predict.py                # Model inference
├── BenchmarkDatasetFolder/
│   ├── HumanEval/data.csv        # 5,893 code tasks
│   ├── GSM8K/data.csv            # 6,142 math problems
│   └── MMLU/data.csv             # Knowledge questions
├── data/
│   └── features.csv              # Training data (23 rows)
├── models/
│   └── xgb_model.json            # Trained XGBoost
├── logs/                         # JSON run logs
├── .env                          # API keys + config
├── requirements.txt              # Python dependencies
└── README.md                     # This file
```

---

## 🔑 Key Commands

```powershell
# Environment setup
python -m venv venv
.\venv\Scripts\Activate.ps1
pip install -r requirements.txt

# Run tasks
python Agent_Monitor/run_with_monitor.py          # Single prompt
python Agent_Monitor/benchmark_runner.py          # Generate data
python Trainer/xgb_trainer.py                     # Train model
python Trainer/predict.py                         # Predict score

# Switch LLM provider
# In .env: LLM_PROVIDER=gemini or ollama

# Ollama setup
pip install ollama
ollama pull llama3
ollama run llama3 "test"
```

---

## 📈 Workflow: Dataset Generation → Model Training

### **Phase 1: Dataset Generation (Friend with Llama/Ollama)**

**Your friend will:**
1. Setup Ollama with local Llama model (see `DATASET_GENERATION_GUIDE.md`)
2. Run benchmark evaluation:
   ```powershell
   python Trainer/evaluate_mas_on_benchmarks.py
   # Choose 20-50 samples per benchmark
   ```
3. Share generated file: `data/mas_benchmark_results.csv`

**Time**: 2-8 hours (depending on sample size)  
**Cost**: FREE (local model)

---

### **Phase 2: Model Training (You)**

**After receiving dataset from friend:**

1. **Copy dataset to your system:**
   ```powershell
   # Place mas_benchmark_results.csv in data/ folder
   ```

2. **Train XGBoost model:**
   ```powershell
   .\venv\Scripts\Activate.ps1
   python Trainer/xgb_trainer_mas.py
   ```

3. **Test predictions:**
   ```powershell
   python Trainer/predict_mas.py
   ```

4. **Deploy model:**
   - Predict MAS_score for new configurations
   - Optimize MAS design based on predictions
   - A/B test different agent combinations

**Time**: 10 minutes  
**Cost**: FREE

---

### **Why This Workflow?**

✅ **Friend has GPU/free time** → Generates expensive benchmark data  
✅ **You get trained model** → No API costs for you  
✅ **Everyone benefits** → Collaborative approach to AI research  

See `DATASET_GENERATION_GUIDE.md` for complete instructions!

---

## 📝 License

MIT License - See repository for details

## 🤝 Contributing

Contributions welcome! Please submit PRs to the `shruthi` branch.

## 📧 Contact

**Author**: Kumaraswamy Bakkashetti  
**Repository**: https://github.com/KumaraswamyBakkashetti/3-1project  
**Branch**: shruthi

---

**Last Updated**: October 8, 2025  
**Version**: 2.0 (Ollama-ready)
