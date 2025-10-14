from fastapi import FastAPI, HTTPException, Depends
from fastapi.middleware.cors import CORSMiddleware
from fastapi.security import HTTPBearer, HTTPAuthorizationCredentials
from pydantic import BaseModel
from datetime import datetime, timedelta
from pathlib import Path
import sys
import jwt
import json
import os
from dotenv import load_dotenv

# Load environment variables
load_dotenv()

ROOT_PATH = Path(__file__).parent.parent
AGENT_MONITOR_PATH = ROOT_PATH / "AgentMonitor"
sys.path.insert(0, str(AGENT_MONITOR_PATH))

from database import Database

app = FastAPI(title="AgentMonitor API")
security = HTTPBearer()
db = Database()

SECRET_KEY = os.getenv("SECRET_KEY", "agentmonitor-secret-key-2025")

# Get CORS origins from environment variable
cors_origins = os.getenv("CORS_ORIGINS", "http://localhost:3000").split(",")

app.add_middleware(
    CORSMiddleware,
    allow_origins=cors_origins,
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

class LoginRequest(BaseModel):
    username: str
    password: str

class RegisterRequest(BaseModel):
    username: str
    password: str
    role: str = "user"  # default to user role

class RunRequest(BaseModel):
    task: str
    code: str = ""

def create_token(username, role):
    payload = {
        "username": username,
        "role": role,
        "exp": datetime.utcnow() + timedelta(days=1)
    }
    return jwt.encode(payload, SECRET_KEY, algorithm="HS256")

def verify_token(credentials: HTTPAuthorizationCredentials = Depends(security)):
    try:
        payload = jwt.decode(credentials.credentials, SECRET_KEY, algorithms=["HS256"])
        return payload
    except:
        raise HTTPException(status_code=401, detail="Invalid token")

def calculate_graph_metrics(graph_edges: list, num_nodes: int) -> dict:
    """Calculate actual graph metrics from edges"""
    import networkx as nx
    import numpy as np
    
    if not graph_edges or num_nodes == 0:
        return {
            "clustering_coefficient": 0.0,
            "transitivity": 0.0,
            "avg_degree_centrality": 0.0,
            "avg_betweenness_centrality": 0.0,
            "avg_closeness_centrality": 0.0,
            "pagerank_entropy": 0.0,
            "heterogeneity_score": 0.0
        }
    
    # Build directed graph
    G = nx.DiGraph()
    
    # Map agent names to node indices
    agent_names = sorted(set([e[0] for e in graph_edges] + [e[1] for e in graph_edges]))
    name_to_idx = {name: i for i, name in enumerate(agent_names)}
    
    G.add_nodes_from(range(len(agent_names)))
    
    # Add edges
    for from_agent, to_agent in graph_edges:
        if from_agent in name_to_idx and to_agent in name_to_idx:
            G.add_edge(name_to_idx[from_agent], name_to_idx[to_agent])
    
    # Calculate metrics
    try:
        # Clustering (convert to undirected)
        G_undirected = G.to_undirected()
        clustering = nx.average_clustering(G_undirected)
        transitivity = nx.transitivity(G_undirected)
        
        # Centrality
        degree_cent = nx.degree_centrality(G)
        betweenness_cent = nx.betweenness_centrality(G)
        closeness_cent = nx.closeness_centrality(G)
        
        avg_degree = np.mean(list(degree_cent.values()))
        avg_betweenness = np.mean(list(betweenness_cent.values()))
        avg_closeness = np.mean(list(closeness_cent.values()))
        
        # PageRank entropy
        pagerank = nx.pagerank(G)
        pr_values = np.array(list(pagerank.values()))
        pr_values = pr_values[pr_values > 0]  # Remove zeros
        pagerank_entropy = -np.sum(pr_values * np.log(pr_values + 1e-10))
        
        # Heterogeneity (variance in degrees)
        degrees = [G.degree(n) for n in G.nodes()]
        heterogeneity = np.std(degrees) / (np.mean(degrees) + 1e-10)
        
    except Exception as e:
        print(f"⚠️ Graph metric calculation failed: {e}")
        clustering = transitivity = avg_degree = avg_betweenness = 0.0
        avg_closeness = pagerank_entropy = heterogeneity = 0.0
    
    return {
        "clustering_coefficient": clustering,
        "transitivity": transitivity,
        "avg_degree_centrality": avg_degree,
        "avg_betweenness_centrality": avg_betweenness,
        "avg_closeness_centrality": avg_closeness,
        "pagerank_entropy": pagerank_entropy,
        "heterogeneity_score": heterogeneity
    }

def extract_features_from_monitor(monitor_data: dict) -> dict:
    """Extract 16 features from monitoring data"""
    agent_stats = monitor_data.get("agent_stats", {})
    graph_edges = monitor_data.get("graph_edges", [])
    
    # System features (6)
    all_scores, all_latencies = [], []
    all_tokens, num_enhanced, max_loops = 0, 0, 0
    
    for stats in agent_stats.values():
        all_scores.extend(stats.get("scores", []))
        all_latencies.extend(stats.get("latencies", []))
        all_tokens += stats.get("token_usage", 0)
        num_enhanced += stats.get("enhancement_triggered", 0)
        max_loops = max(max_loops, len(stats.get("latencies", [])))
    
    features = {
        "avg_personal_score": sum(all_scores) / len(all_scores) if all_scores else 0.0,
        "min_personal_score": min(all_scores) if all_scores else 0.0,
        "max_loops": max_loops,
        "total_latency": sum(all_latencies),
        "total_token_usage": all_tokens,
        "num_agents_triggered_enhancement": num_enhanced,
        
        # Graph features (9)
        "num_nodes": len(agent_stats),
        "num_edges": len(graph_edges),
    }
    
    # Calculate real graph metrics
    graph_metrics = calculate_graph_metrics(graph_edges, len(agent_stats))
    features.update(graph_metrics)
    
    # Collective score (1)
    features["collective_score"] = sum(all_scores) / len(all_scores) if all_scores else 0.0
    
    print(f"✅ Extracted {len(features)} features")
    
    return features


@app.post("/api/login")
async def login(request: LoginRequest):
    print(f"Login attempt - Username: {request.username}, Password length: {len(request.password)}")
    user = db.verify_user(request.username, request.password)
    print(f"User found: {user is not None}")
    if not user:
        raise HTTPException(status_code=401, detail="Invalid credentials")
    token = create_token(user["username"], user["role"])
    return {"token": token, "username": user["username"], "role": user["role"]}

@app.post("/api/register")
async def register(request: RegisterRequest):
    # Check if user already exists
    existing = db.users.find_one({"username": request.username})
    if existing:
        raise HTTPException(status_code=400, detail="Username already exists")
    
    # Create new user
    new_user = {
        "username": request.username,
        "password": db.hash_password(request.password),
        "role": request.role if request.role in ["user", "admin"] else "user",
        "created_at": datetime.now()
    }
    db.users.insert_one(new_user)
    
    # Create token for immediate login
    token = create_token(new_user["username"], new_user["role"])
    return {"token": token, "username": new_user["username"], "role": new_user["role"]}

@app.get("/api/user/me")
async def get_current_user(user = Depends(verify_token)):
    return user

@app.post("/api/run_mas")
async def run_mas(request: RunRequest, user = Depends(verify_token)):
    try:
        print(f"MAS execution request from {user['username']}: {request.task[:50]}...")
        
        # Import necessary components from AgentMonitor
        from AgentMonitor import EnhancedAgentMonitor, CodeGenerationMAS, MASPredictor
        from AgentMonitor.gemini_api import gemini_call
        
        # Use gemini_call as LLM (with automatic key rotation)
        llm = gemini_call
        
        # Determine if this is an enhancement request or initial request
        is_enhancement = bool(request.code and request.code.strip())
        
        if is_enhancement:
            print(f"🔄 Enhancement mode - improving existing code ({len(request.code)} chars)")
            # Enhancement: Faster configuration for Llama
            mas = CodeGenerationMAS(
                llm=llm,
                threshold=0.75,  # Reasonable threshold
                max_retries=1    # Reduced retries for speed
            )
            
            monitor = EnhancedAgentMonitor(
                llm=llm,
                threshold=0.75,  # Reasonable threshold
                max_retries=1,   # Single enhancement loop for speed
                debug=False
            )
            
            # Enhance the existing code
            enhancement_task = f"{request.task}\n\nExisting code to improve:\n{request.code}\n\nPlease enhance this code with better quality, optimization, and best practices."
            print(f"Running enhancement on task...")
            result = await mas.run(enhancement_task, monitor=monitor)
            
        else:
            print(f"✨ Initial mode - generating new code")
            # Initial: RESTORED to this morning's working configuration
            mas = CodeGenerationMAS(
                llm=llm,
                threshold=0.75,  # RESTORED - was working this morning
                max_retries=1    # RESTORED - was working this morning
            )
            
            monitor = EnhancedAgentMonitor(
                llm=llm,
                threshold=0.75,  # RESTORED - was working this morning
                max_retries=1,   # RESTORED - was working this morning
                debug=False
            )
            
            print(f"✅ RESTORED MODE: threshold=0.75, max_retries=1 (like this morning)")
            print(f"Running MAS on task: {request.task[:60]}...")
            result = await mas.run(request.task, monitor=monitor)
        
        print(f"🔍 DEBUG - MAS execution completed")
        print(f"🔍 DEBUG - Result type: {type(result)}")
        print(f"🔍 DEBUG - Result length: {len(str(result))}")
        print(f"🔍 DEBUG - Result preview: {str(result)[:200]}")
        
        # STEP 2: Extract features from monitor_data
        monitor_data = monitor.monitor_data
        
        # Debug: Check what agents actually generated
        print(f"\n🔍 DEBUG - Agent Conversations:")
        for agent_name, stats in monitor_data.get("agent_stats", {}).items():
            conversations = stats.get("conversations", [])
            if conversations:
                last_conv = conversations[-1]
                print(f"   {agent_name}:")
                print(f"      - Output length: {len(last_conv.get('output', ''))}")
                print(f"      - Output preview: {last_conv.get('output', '')[:100]}...")
                print(f"      - Score: {last_conv.get('score', 0)}")
        
        features = extract_features_from_monitor(monitor_data)
        
        # STEP 3: Load predictor and predict score
        print("Loading predictor model...")
        predictor = MASPredictor()
        model_path = AGENT_MONITOR_PATH / "models" / "mas_predictor.pkl"
        
        if not model_path.exists():
            raise HTTPException(status_code=500, detail="Model not found. Run training first.")
        
        predictor.load(model_path)
        predicted_score = predictor.predict(features)
        
        print(f"{'Enhanced' if is_enhancement else 'Initial'} predicted score: {predicted_score:.4f}")
        
        # Store initial results
        initial_code = None
        initial_score = None
        initial_monitor_data = None
        
        # STEP 4: Extract clean code
        print(f"🔍 DEBUG - Raw result type: {type(result)}")
        print(f"🔍 DEBUG - Raw result value: {result}")
        
        # The MAS returns code as a string, but might be wrapped in dict
        if isinstance(result, dict):
            print(f"🔍 DEBUG - Result is dict with keys: {result.keys()}")
            if 'output' in result:
                clean_code = result['output']
            elif 'code' in result:
                clean_code = result['code']
            elif 'result' in result:
                clean_code = result['result']
            else:
                # Try to get the first string value
                clean_code = str(result)
        elif isinstance(result, str):
            clean_code = result
        else:
            clean_code = str(result)
        
        print(f"✅ Code extracted ({len(clean_code)} characters)")
        print(f"🔍 DEBUG - Clean code preview: {clean_code[:200]}")
        
        # Store initial code and score before enhancement
        initial_code = clean_code
        initial_score = predicted_score
        initial_monitor_data = monitor_data
        
        # STEP 5: Optional auto-enhancement if score is too low (only on initial run)
        auto_enhanced = False
        enhancement_loops = 0
        # OPTIMIZED AUTO-ENHANCEMENT - faster but still functional for research
        # Reduced retries from 3→1 and threshold from 0.8→0.75 for speed
        if not is_enhancement and predicted_score < 0.75:
            print(f"⚠️ Score {predicted_score:.4f} below threshold 0.75, triggering auto-enhancement...")
            try:
                # Re-run with enhancement (OPTIMIZED for speed)
                enhanced_mas = CodeGenerationMAS(
                    llm=llm,
                    threshold=0.75,  # Reduced from 0.8 for speed
                    max_retries=1    # Reduced from 3 for speed (was causing delays)
                )
                
                enhanced_monitor = EnhancedAgentMonitor(
                    llm=llm,
                    threshold=0.75,  # Reduced from 0.8 for speed
                    max_retries=1,   # Reduced from 2 for speed
                    debug=False
                )
                
                enhancement_task = f"{request.task}\n\nExisting code to improve:\n{clean_code}\n\nPlease enhance this code with better quality, optimization, and best practices."
                enhanced_result = await enhanced_mas.run(enhancement_task, monitor=enhanced_monitor)
                
                # Extract enhanced features and score
                enhanced_monitor_data = enhanced_monitor.monitor_data
                enhanced_features = extract_features_from_monitor(enhanced_monitor_data)
                enhanced_score = predictor.predict(enhanced_features)
                
                print(f"🎯 Auto-enhanced score: {enhanced_score:.4f} (improvement: +{enhanced_score - predicted_score:.4f})")
                
                # Use enhanced version if it's better
                if enhanced_score > predicted_score:
                    if isinstance(enhanced_result, dict) and 'output' in enhanced_result:
                        clean_code = enhanced_result['output']
                    elif isinstance(enhanced_result, str):
                        clean_code = enhanced_result
                    else:
                        clean_code = str(enhanced_result)
                    
                    features = enhanced_features
                    predicted_score = enhanced_score
                    monitor_data = enhanced_monitor_data
                    auto_enhanced = True
                    enhancement_loops = 1
                    print("✅ Using auto-enhanced version")
                else:
                    print("⚠️ Auto-enhancement didn't improve score, keeping original")
            except Exception as e:
                print(f"⚠️ Auto-enhancement failed: {e}, keeping original")
        
        # STEP 6: Save to database
        run_id = db.save_run(
            user_id=user["username"],
            username=user["username"],
            task=request.task,
            code=clean_code,
            predicted_score=float(predicted_score),
            features=features,
            monitor_data=monitor_data
        )
        
        print(f"📤 Returning response:")
        print(f"   - predicted_score: {predicted_score}")
        print(f"   - code length: {len(clean_code)}")
        print(f"   - code preview: {clean_code[:100]}...")
        print(f"   - is_enhancement: {is_enhancement}")
        print(f"   - auto_enhanced: {auto_enhanced}")
        
        return {
            "run_id": str(run_id),
            "predicted_score": float(predicted_score),
            "initial_score": float(initial_score) if initial_score else float(predicted_score),
            "features": features,
            "result": clean_code,  # Return clean code, not raw result
            "code": clean_code,  # Also include as 'code' for clarity
            "initial_code": initial_code,  # Original code before enhancement
            "final_code": clean_code,  # Code after enhancement (if any)
            "is_enhancement": is_enhancement,  # Flag to indicate if this was an enhancement
            "auto_enhanced": auto_enhanced,  # Flag to indicate if auto-enhancement was applied
            "enhancement_loops": enhancement_loops,  # Number of enhancement iterations
            "monitor_data": monitor_data  # Full monitoring data for admin view
        }
    except Exception as e:
        print(f"ERROR in run_mas: {str(e)}")
        import traceback
        traceback.print_exc()
        raise HTTPException(status_code=500, detail=str(e))

@app.get("/api/runs/user")
async def get_user_runs(user = Depends(verify_token)):
    runs = db.get_user_runs(user["username"])
    for run in runs:
        run["_id"] = str(run["_id"])
    return runs

@app.get("/api/runs/all")
async def get_all_runs(user = Depends(verify_token)):
    if user["role"] != "admin":
        raise HTTPException(status_code=403, detail="Admin only")
    runs = db.get_all_runs()
    for run in runs:
        run["_id"] = str(run["_id"])
    return runs

@app.get("/api/run/{run_id}")
async def get_run(run_id: str, user = Depends(verify_token)):
    run = db.get_run(run_id)
    if not run:
        raise HTTPException(status_code=404, detail="Run not found")
    if user["role"] != "admin" and run["username"] != user["username"]:
        raise HTTPException(status_code=403, detail="Not authorized")
    run["_id"] = str(run["_id"])
    return run

@app.get("/api/export_csv")
async def export_csv(user = Depends(verify_token)):
    if user["role"] != "admin":
        raise HTTPException(status_code=403, detail="Admin only")
    csv_data = db.export_to_csv()
    return {"csv": csv_data}

if __name__ == "__main__":
    import uvicorn
    print("AgentMonitor API - http://localhost:8080")
    uvicorn.run(app, host="0.0.0.0", port=8080)
