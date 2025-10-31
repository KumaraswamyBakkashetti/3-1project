# AgentMonitor API Documentation

## Base URL
```
http://localhost:8080
```

---

## Endpoints

### 1. Submit Task

**POST** `/submit-task`

Submit a coding task for Multi-Agent System processing.

#### Request Body
```json
{
  "userId": "string (required)",
  "task": "string (required) - The coding task description",
  "benchmarkName": "string (optional) - 'Custom', 'GSM8k', 'HumanEval', 'MMLU'"
}
```

#### Example Request
```bash
curl -X POST http://localhost:8080/submit-task \
  -H "Content-Type: application/json" \
  -d '{
    "userId": "user123",
    "task": "Write a Python function to find all prime numbers up to n using the Sieve of Eratosthenes algorithm",
    "benchmarkName": "Custom"
  }'
```

#### Response (200 OK)
```json
{
  "taskId": "task_67452f5e3a1b4c9d8e0a1b2c",
  "userId": "user123",
  "task": "Write a Python function...",
  "benchmarkName": "Custom",
  "timestamp": "2025-10-31T14:30:00.123Z",
  
  "initialCode": "def sieve_of_eratosthenes(n):\n    if n < 2:\n        return []\n    ...",
  "enhancedCode": "def sieve_of_eratosthenes(n: int) -> list[int]:\n    \"\"\"...\"\"\"\n    ...",
  
  "initialScore": 0.72,
  "enhancedScore": 0.89,
  "autoEnhanced": true,
  
  "features": {
    "response_time_ms": 8432.5,
    "num_retries": 0,
    "total_tokens": 2845,
    "output_length": 1234,
    "num_agents": 4,
    "num_edges": 6,
    "avg_degree": 3.0,
    "clustering_coefficient": 0.667,
    "avg_pagerank": 0.25,
    "graph_density": 0.5,
    "output_diversity": 0.42,
    "consensus_score": 0.85,
    "refinement_cycles": 1,
    "knowledge_sharing": 0.75,
    "specialization_score": 0.68,
    "coordination_efficiency": 0.82
  },
  
  "monitorData": {
    "threshold": 0.75,
    "max_retries": 1,
    "auto_enhanced": true,
    "agent_stats": {
      "Analyzer": { "execution_count": 1, "avg_time": 2.1 },
      "Architect": { "execution_count": 1, "avg_time": 2.3 },
      "Coder": { "execution_count": 1, "avg_time": 2.8 },
      "Optimizer": { "execution_count": 1, "avg_time": 1.9 }
    },
    "enhancement_history": []
  }
}
```

#### Response Fields

| Field | Type | Description |
|-------|------|-------------|
| `taskId` | string | Unique task identifier |
| `initialCode` | string | Fast initial version (1 agent, ~5-10s) |
| `enhancedCode` | string | Optimized version (4 agents, ~15-30s) |
| `initialScore` | float | XGBoost prediction (0.0-1.0) for initial code |
| `enhancedScore` | float | XGBoost prediction for enhanced code |
| `autoEnhanced` | boolean | `true` if enhanced > initial, `false` if initial kept |
| `features` | object | 16 ML features extracted by monitor |
| `monitorData` | object | Agent interaction data |

#### Error Responses

**400 Bad Request** - Missing required fields
```json
{
  "detail": "userId and task are required"
}
```

**500 Internal Server Error** - Processing failure
```json
{
  "detail": "Error message here"
}
```

---

### 2. Get Task History

**GET** `/task-history/{userId}`

Retrieve all tasks submitted by a user.

#### Path Parameters
- `userId` (string, required) - User identifier

#### Example Request
```bash
curl http://localhost:8080/task-history/user123
```

#### Response (200 OK)
```json
[
  {
    "taskId": "task_67452f5e3a1b4c9d8e0a1b2c",
    "task": "Write a Python function...",
    "timestamp": "2025-10-31T14:30:00.123Z",
    "benchmarkName": "Custom",
    "initialScore": 0.72,
    "enhancedScore": 0.89,
    "autoEnhanced": true
  },
  {
    "taskId": "task_67452e4d2a0b3c8d7e9a0b1c",
    "task": "Implement binary search...",
    "timestamp": "2025-10-31T13:15:00.456Z",
    "benchmarkName": "HumanEval",
    "initialScore": 0.68,
    "enhancedScore": 0.85,
    "autoEnhanced": true
  }
]
```

#### Response Fields
Array of task objects with:
- `taskId` - Unique identifier
- `task` - Task description
- `timestamp` - Submission time
- `benchmarkName` - Dataset source
- `initialScore` - Initial code quality (0.0-1.0)
- `enhancedScore` - Enhanced code quality
- `autoEnhanced` - Whether enhancement improved quality

---

### 3. Get Analytics

**GET** `/analytics/{userId}`

Get performance analytics and trends for a user.

#### Path Parameters
- `userId` (string, required) - User identifier

#### Example Request
```bash
curl http://localhost:8080/analytics/user123
```

#### Response (200 OK)
```json
{
  "userId": "user123",
  "totalTasks": 45,
  "avgInitialScore": 0.68,
  "avgEnhancedScore": 0.84,
  "enhancementRate": 0.88,
  "avgResponseTime": 18234.5,
  
  "scoreDistribution": {
    "initial": {
      "0.0-0.2": 2,
      "0.2-0.4": 5,
      "0.4-0.6": 12,
      "0.6-0.8": 18,
      "0.8-1.0": 8
    },
    "enhanced": {
      "0.0-0.2": 0,
      "0.2-0.4": 1,
      "0.4-0.6": 4,
      "0.6-0.8": 15,
      "0.8-1.0": 25
    }
  },
  
  "featureImportance": {
    "num_agents": 0.18,
    "clustering_coefficient": 0.15,
    "coordination_efficiency": 0.14,
    "output_diversity": 0.12,
    "consensus_score": 0.11,
    "avg_pagerank": 0.10,
    "refinement_cycles": 0.08,
    "graph_density": 0.07,
    "knowledge_sharing": 0.05
  },
  
  "trendsOverTime": [
    {
      "date": "2025-10-31",
      "avgScore": 0.82,
      "taskCount": 12
    },
    {
      "date": "2025-10-30",
      "avgScore": 0.79,
      "taskCount": 15
    }
  ]
}
```

#### Response Fields

| Field | Type | Description |
|-------|------|-------------|
| `totalTasks` | int | Total tasks submitted |
| `avgInitialScore` | float | Average initial code quality |
| `avgEnhancedScore` | float | Average enhanced code quality |
| `enhancementRate` | float | % of tasks where enhancement improved quality |
| `avgResponseTime` | float | Average processing time (ms) |
| `scoreDistribution` | object | Score buckets for initial vs enhanced |
| `featureImportance` | object | XGBoost feature weights |
| `trendsOverTime` | array | Daily performance trends |

---

### 4. Get Task Details

**GET** `/task/{taskId}`

Retrieve complete details for a specific task.

#### Path Parameters
- `taskId` (string, required) - Task identifier

#### Example Request
```bash
curl http://localhost:8080/task/task_67452f5e3a1b4c9d8e0a1b2c
```

#### Response (200 OK)
Same structure as `/submit-task` response - full task details including code, scores, features, and monitor data.

---

### 5. Health Check

**GET** `/health`

Check API server status.

#### Example Request
```bash
curl http://localhost:8080/health
```

#### Response (200 OK)
```json
{
  "status": "healthy",
  "version": "1.0.0",
  "timestamp": "2025-10-31T14:30:00.123Z",
  "services": {
    "mongodb": "connected",
    "predictor": "loaded",
    "gemini": "configured",
    "groq": "configured"
  }
}
```

---

## Feature Extraction Details

The monitor automatically extracts 16 features during task processing:

### System Features (4)
1. **response_time_ms** - Total agent execution time
2. **num_retries** - Enhancement loop iterations
3. **total_tokens** - LLM token consumption
4. **output_length** - Generated code character count

### Graph Features (6)
5. **num_agents** - Number of agents in MAS
6. **num_edges** - Inter-agent connections
7. **avg_degree** - Average agent connectivity
8. **clustering_coefficient** - Agent grouping measure
9. **avg_pagerank** - Agent importance distribution
10. **graph_density** - Network completeness (0.0-1.0)

### Collective Intelligence Features (6)
11. **output_diversity** - Code variation across agents
12. **consensus_score** - Agent agreement level
13. **refinement_cycles** - Iterative improvement count
14. **knowledge_sharing** - Cross-agent information flow
15. **specialization_score** - Role focus intensity
16. **coordination_efficiency** - Collaboration smoothness

---

## XGBoost Prediction

The system uses a trained XGBoost model to predict code quality (0.0-1.0 score):

```python
# Prediction flow
features = extract_features_from_monitor(monitor_data)
score = predictor.predict(features)

# Score interpretation
# 0.0-0.4: Poor quality (needs major revision)
# 0.4-0.6: Acceptable (minor improvements needed)
# 0.6-0.8: Good quality (ready for review)
# 0.8-1.0: Excellent (production-ready)
```

---

## Quality Gate Logic

The system intelligently selects the best code version:

```python
if enhanced_score > initial_score:
    # Enhanced version is better
    final_code = enhanced_code
    auto_enhanced = True
else:
    # Initial version is better (enhancement failed)
    final_code = initial_code
    auto_enhanced = False
```

**When enhancement fails:**
- Over-complicated solution
- Gemini safety blocks
- Timeout or errors
- Output too short (<100 chars)

---

## Rate Limits

### Gemini API
- **Free tier:** 60 requests/minute
- **With multiple keys:** Automatic rotation extends capacity

### Groq API (FREE)
- **Rate limit:** 30 requests/minute
- **Cost:** $0 (100% FREE)
- **Usage:** Code judging & feedback only

### Backend Server
- **No hard limit** - async FastAPI handles concurrent requests
- **Recommended:** <10 concurrent tasks for optimal performance

---

## Error Handling

All endpoints return standard HTTP status codes:

| Code | Meaning | Response |
|------|---------|----------|
| 200 | Success | Task data or results |
| 400 | Bad Request | Missing/invalid parameters |
| 404 | Not Found | Task or user not found |
| 500 | Server Error | Processing failure |
| 503 | Service Unavailable | LLM API down |

Example error response:
```json
{
  "detail": "Task not found: task_invalid123",
  "timestamp": "2025-10-31T14:30:00.123Z",
  "path": "/task/task_invalid123"
}
```

---

## WebSocket Support (Future)

Currently not implemented. Planned for real-time updates:

```javascript
// Future feature
const ws = new WebSocket('ws://localhost:8080/ws/task-progress');
ws.onmessage = (event) => {
  const progress = JSON.parse(event.data);
  // { phase: 'initial', status: 'completed', score: 0.72 }
  // { phase: 'enhanced', status: 'in-progress', agent: 'Coder' }
};
```

---

## Authentication (Future)

Currently not implemented. Planned for production:

```bash
# Future feature
curl -X POST http://localhost:8080/submit-task \
  -H "Authorization: Bearer YOUR_JWT_TOKEN" \
  -H "Content-Type: application/json" \
  -d '{ ... }'
```

---

## Best Practices

### 1. Task Description Quality
```json
// ❌ Bad: Too vague
{ "task": "Write a function" }

// ✅ Good: Specific requirements
{
  "task": "Write a Python function to find all prime numbers up to n using the Sieve of Eratosthenes. Include input validation, unit tests, and docstring."
}
```

### 2. Language Specification
```json
// Auto-detected from task text
{ "task": "Write a Java function..." }  // → language='java'
{ "task": "Implement in C++..." }       // → language='cpp'
{ "task": "Create a Python..." }        // → language='python' (default)
```

### 3. Monitoring Task Progress
```javascript
// Poll for task completion
const checkTask = async (taskId) => {
  const response = await fetch(`/task/${taskId}`);
  const data = await response.json();
  
  if (data.autoEnhanced) {
    console.log('Enhanced version is better');
  } else {
    console.log('Initial version kept (enhancement failed)');
  }
};
```

---

## Code Examples

### Python Client
```python
import requests

# Submit task
response = requests.post('http://localhost:8080/submit-task', json={
    'userId': 'user123',
    'task': 'Write a binary search function in Python',
    'benchmarkName': 'Custom'
})

result = response.json()
print(f"Initial score: {result['initialScore']}")
print(f"Enhanced score: {result['enhancedScore']}")
print(f"Auto-enhanced: {result['autoEnhanced']}")

# Get analytics
analytics = requests.get(f"http://localhost:8080/analytics/user123").json()
print(f"Total tasks: {analytics['totalTasks']}")
print(f"Avg enhancement: {analytics['avgEnhancedScore']}")
```

### JavaScript Client
```javascript
// Submit task
const submitTask = async (userId, task) => {
  const response = await fetch('http://localhost:8080/submit-task', {
    method: 'POST',
    headers: { 'Content-Type': 'application/json' },
    body: JSON.stringify({ userId, task, benchmarkName: 'Custom' })
  });
  
  const result = await response.json();
  console.log('Initial:', result.initialCode);
  console.log('Enhanced:', result.enhancedCode);
  return result;
};

// Get task history
const getHistory = async (userId) => {
  const response = await fetch(`http://localhost:8080/task-history/${userId}`);
  const history = await response.json();
  return history;
};
```

---

## Changelog

### v1.0.0 (2025-10-31)
- Initial production release
- Two-phase workflow (initial + enhanced)
- Dual-LLM architecture (Gemini + Groq)
- XGBoost performance prediction
- Quality gate intelligence
- Real-time analytics dashboard
- MAS-agnostic monitoring

---

## Support

For API questions or issues:
- **GitHub Issues:** [Report bugs](https://github.com/KumaraswamyBakkashetti/3-1project/issues)
- **Documentation:** [ARCHITECTURE.md](ARCHITECTURE.md)
- **README:** [README.md](README.md)
