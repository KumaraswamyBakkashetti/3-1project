from fastapi import FastAPI, HTTPException, Depends, BackgroundTasks
from fastapi.middleware.cors import CORSMiddleware
from fastapi.security import HTTPBearer, HTTPAuthorizationCredentials
from pydantic import BaseModel
from datetime import datetime, timedelta
from pathlib import Path
import sys
try:
    import jwt
except Exception:
    # jwt (PyJWT) may not be installed in all environments. Provide a minimal fallback
    jwt = None
import json
import os
from dotenv import load_dotenv

# Load environment variables from backend/.env
# This ensures the correct API key is loaded
load_dotenv()

# CRITICAL: Ensure Gemini API key is available
GEMINI_API_KEY = os.getenv('GEMINI_API_KEY')
if not GEMINI_API_KEY:
    print("⚠️  WARNING: GEMINI_API_KEY not found in environment!")
    print("   Set it using: $env:GEMINI_API_KEY='your_key_here'")
else:
    print(f"✅ Gemini API Key loaded: {GEMINI_API_KEY[:25]}...{GEMINI_API_KEY[-10:]}")
    # Set it in environment to ensure all modules use it
    os.environ['GEMINI_API_KEY'] = GEMINI_API_KEY

ROOT_PATH = Path(__file__).parent.parent
# Ensure the project root is on sys.path so `import AgentMonitor` works whether
# the backend is started from the `backend/` folder or the repository root.
sys.path.insert(0, str(ROOT_PATH))

from database import Database

# Initialize XGBoost predictor
try:
    from AgentMonitor.models.predictor import MASPredictor
    MODEL_PATH = ROOT_PATH / "AgentMonitor" / "models" / "mas_predictor.pkl"
    predictor = MASPredictor(model_path=MODEL_PATH)
    if MODEL_PATH.exists():
        predictor.load()  # Fixed: method is called 'load()' not 'load_model()'
        print("✅ XGBoost model loaded successfully")
    else:
        print(f"⚠️ XGBoost model not found at {MODEL_PATH}")
        predictor = None
except Exception as e:
    print(f"⚠️ XGBoost model failed to load: {e}")
    print("   Will use agent score averaging as fallback")
    predictor = None

app = FastAPI(title="AgentMonitor API")
security = HTTPBearer()
db = Database()

SECRET_KEY = os.getenv("SECRET_KEY", "agentmonitor-secret-key-2025")

# Get CORS origins from environment variable
cors_origins = os.getenv("CORS_ORIGINS", "http://localhost:3000").split(",")

# Add CORS middleware with explicit configuration
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],  # Allow all origins for development
    allow_credentials=True,
    allow_methods=["GET", "POST", "PUT", "DELETE", "OPTIONS"],
    allow_headers=["*"],
    expose_headers=["*"],
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
    language: str = "auto"  # NEW: Support multiple languages; default to 'auto' so LLM can detect
    use_full_mas: bool = False  # NEW: Enable full 4-agent MAS mode for graph metrics

def create_token(username, role):
    payload = {
        "username": username,
        "role": role,
        "exp": datetime.utcnow() + timedelta(days=1)
    }
    if jwt:
        return jwt.encode(payload, SECRET_KEY, algorithm="HS256")
    else:
        # Development fallback: return a simple JSON string (NOT secure)
        return json.dumps({"username": username, "role": role, "exp": payload["exp"].isoformat()})

def verify_token(credentials: HTTPAuthorizationCredentials = Depends(security)):
    try:
        if jwt:
            payload = jwt.decode(credentials.credentials, SECRET_KEY, algorithms=["HS256"])
            return payload
        else:
            # Try to parse our development fallback token
            try:
                data = json.loads(credentials.credentials)
                return {"username": data.get("username"), "role": data.get("role")}
            except Exception:
                raise HTTPException(status_code=401, detail="Invalid token or jwt not installed")
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


# Health check endpoint
@app.get("/")
async def root():
    """Health check endpoint"""
    return {
        "status": "running",
        "service": "AgentMonitor API",
        "version": "1.0",
        "endpoints": {
            "login": "/api/login",
            "register": "/api/register",
            "run_mas": "/api/run_mas"
        }
    }

@app.get("/api/health")
async def health():
    """Detailed health check"""
    return {
        "status": "healthy",
        "gemini_api_key": "configured" if GEMINI_API_KEY else "missing",
        "xgboost_model": "loaded" if predictor else "not loaded",
        "database": "connected"
    }

@app.post("/api/login")
async def login(request: LoginRequest):
    """Authenticate user and return JWT token"""
    try:
        print(f"Login attempt - Username: {request.username}, Password length: {len(request.password)}")
        user = db.verify_user(request.username, request.password)
        print(f"User found: {user is not None}")
        if not user:
            raise HTTPException(status_code=401, detail="Invalid credentials")
        token = create_token(user["username"], user["role"])
        return {"token": token, "username": user["username"], "role": user["role"]}
    except HTTPException:
        raise
    except Exception as e:
        print(f"❌ Login error: {e}")
        raise HTTPException(status_code=500, detail=f"Login failed: {str(e)}")

@app.post("/api/register")
async def register(request: RegisterRequest):
    """Register new user and return JWT token"""
    try:
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
    except HTTPException:
        raise
    except Exception as e:
        print(f"❌ Registration error: {e}")
        raise HTTPException(status_code=500, detail=f"Registration failed: {str(e)}")

@app.get("/api/user/me")
async def get_current_user(user = Depends(verify_token)):
    return user

@app.post("/api/run_mas")
async def run_mas(request: RunRequest, user = Depends(verify_token)):
    """
    Main endpoint for code generation with Multi-Agent System.
    
    Handles both initial generation and enhancement requests.
    Uses Gemini for code generation and Groq (free) for scoring.
    """
    try:
        print(f"MAS execution request from {user['username']}: {request.task[:50]}...")
        
        # Validate API keys early
        if not GEMINI_API_KEY:
            raise HTTPException(
                status_code=503, 
                detail="Gemini API key not configured. Please set GEMINI_API_KEY in backend/.env"
            )
        
        # Import necessary components from AgentMonitor
        try:
            from AgentMonitor import EnhancedAgentMonitor, CodeGenerationMAS, MASPredictor
            from AgentMonitor.gemini_api import gemini_call
            from AgentMonitor.groq_api import groq_call
        except ImportError as e:
            print(f"❌ Import error: {e}")
            raise HTTPException(
                status_code=500,
                detail=f"AgentMonitor module import failed: {str(e)}"
            )
        
        # DUAL-LLM SETUP: Gemini for code generation, Groq (FREE) for judging
        llm = gemini_call  # Code generation (powerful model)
        judge_llm = groq_call  # Scoring/feedback (FREE, fast model)
        
        print("🎯 Using dual-LLM: Gemini (generation) + Groq (FREE judging)")
        
        # Determine if this is an enhancement request or initial request
        is_enhancement = bool(request.code and request.code.strip())
        
        if is_enhancement:
            # User clicked "Enhance Again" - just enhance the provided code
            print(f"🔄 Enhancement mode - improving existing code ({len(request.code)} chars)")
            
            mas = CodeGenerationMAS(
                llm=llm,
                language=request.language,
                threshold=0.75,
                max_retries=1
            )
            
            monitor = EnhancedAgentMonitor(
                llm=llm,
                judge_llm=judge_llm,  # Use FREE Groq for judging
                threshold=0.75,
                max_retries=1,
                debug=True
            )
            
            # Keep original task as-is - it already has language specification
            enhancement_task = request.task
            print(f"🔄 Running enhancement with monitoring...")
            
            initial_code = request.code
            
            # Use heuristic for user-provided code (faster, no API call)
            if len(initial_code) > 500:
                initial_score = 0.75
            elif len(initial_code) > 200:
                initial_score = 0.70
            else:
                initial_score = 0.65
            print(f"📊 User code score (heuristic): {initial_score:.3f}")
            
            # Try to enhance
            try:
                result = await mas.run(enhancement_task, monitor=monitor)
                
                if isinstance(result, dict):
                    clean_code = result.get('output') or result.get('code') or str(result)
                else:
                    clean_code = str(result)
                
                # Check if enhancement failed
                if "Error:" in clean_code or "blocked" in clean_code.lower() or len(clean_code) < 100:
                    print(f"⚠️ Enhancement failed, using original code")
                    clean_code = initial_code
                    predicted_score = initial_score  # Use initial score since code didn't improve
                    auto_enhanced = False
                else:
                    # Enhancement succeeded, score the enhanced code
                    try:
                        predicted_score = await monitor._score_output(request.task, clean_code, "EnhancedCode")
                        print(f"📊 Enhanced code score: {predicted_score:.3f}")
                    except:
                        predicted_score = initial_score * 1.1  # Assume 10% improvement
                    auto_enhanced = True
            except Exception as e:
                print(f"⚠️ Enhancement failed: {e}")
                clean_code = initial_code
                predicted_score = initial_score
                auto_enhanced = False
            
            monitor_data = None
            enhancement_loops = 0
            features = None
            
        else:
            # NEW WORKFLOW: Generate initial code, then automatically enhance it
            print(f"✨ Two-step workflow: Initial → Enhanced")
            
            # STEP 1: Generate initial code (FAST, no monitoring)
            print(f"⚡ Step 1/2: Generating initial code...")
            # Detect language from task if not specified
            task_lower = request.task.lower()
            if not request.language or request.language == 'auto':
                # Try to detect language from task text
                if ' java' in task_lower or 'in java' in task_lower:
                    initial_language = 'java'
                elif ' python' in task_lower or 'in python' in task_lower:
                    initial_language = 'python'
                elif 'javascript' in task_lower or ' js' in task_lower:
                    initial_language = 'javascript'
                else:
                    initial_language = 'auto'
            else:
                initial_language = request.language.lower()
            
            print(f"🔍 Detected language: {initial_language}")
            
            # STEP 1: Generate initial code WITH simple monitoring for features
            print(f"⚡ Step 1/2: Generating initial code with basic monitoring...")
            mas_initial = CodeGenerationMAS(
                llm=llm,
                language=initial_language,
                threshold=1.0,  # No enhancement in initial step
                max_retries=0,
                use_full_mas=False  # Fast mode - Coder only
            )
            
            # Create simple monitor for initial code (no enhancement, just feature collection)
            initial_monitor = EnhancedAgentMonitor(
                llm=llm,
                judge_llm=judge_llm,
                threshold=1.0,  # No enhancement trigger
                max_retries=0,
                debug=False
            )
            
            initial_result = await mas_initial.run(request.task, monitor=initial_monitor)
            
            if isinstance(initial_result, dict):
                initial_code = initial_result.get('output') or initial_result.get('code') or str(initial_result)
            else:
                initial_code = str(initial_result)
            
            print(f"✅ Initial code generated: {len(initial_code)} chars")
            
            # Extract features from initial monitoring and predict with XGBoost
            initial_features = extract_features_from_monitor(initial_monitor.monitor_data)
            try:
                # Use global predictor (already loaded)
                if predictor:
                    initial_score = predictor.predict(initial_features)
                    print(f"📊 Initial code XGBoost score: {initial_score:.3f}")
                else:
                    raise Exception("Predictor not loaded")
            except Exception as e:
                print(f"⚠️ XGBoost prediction failed, using heuristic: {e}")
                if len(initial_code) > 500:
                    initial_score = 0.70
                elif len(initial_code) > 200:
                    initial_score = 0.65
                else:
                    initial_score = 0.60
            
            # STEP 2: Automatically enhance with agent-level monitoring
            print(f"🔄 Step 2/2: Enhancing with agent-level monitoring...")
            mas_enhanced = CodeGenerationMAS(
                llm=llm,
                language=initial_language,  # Use same detected language
                threshold=0.75,
                max_retries=1,
                use_full_mas=True  # Use all 4 agents for proper MAS
            )
            
            monitor = EnhancedAgentMonitor(
                llm=llm,
                judge_llm=judge_llm,  # Use FREE Groq for judging
                threshold=0.75,
                max_retries=1,
                debug=True
            )
            
            # Keep the original task as-is (already contains language specification)
            # Don't modify it - Gemini understands "in Java" from the original prompt
            enhancement_task = request.task
            
            try:
                enhanced_result = await mas_enhanced.run(enhancement_task, monitor=monitor)
                
                if isinstance(enhanced_result, dict):
                    clean_code = enhanced_result.get('output') or enhanced_result.get('code') or str(enhanced_result)
                else:
                    clean_code = str(enhanced_result)
                
                # Check if enhancement failed (error message, blocked, or too short)
                enhancement_failed = False
                
                # IMPROVED: Better detection of failed enhancement
                if not clean_code or len(clean_code.strip()) < 50:
                    print(f"⚠️ Enhancement returned empty/very short code, using initial code")
                    clean_code = initial_code
                    auto_enhanced = False
                    enhancement_failed = True
                elif "Error:" in clean_code or "Exception" in clean_code or "Failed" in clean_code:
                    print(f"⚠️ Enhancement returned error message, using initial code")
                    clean_code = initial_code
                    auto_enhanced = False
                    enhancement_failed = True
                elif len(clean_code) < len(initial_code) * 0.3:
                    # Enhanced code is less than 30% of initial - probably a template/fallback
                    print(f"⚠️ Enhanced code ({len(clean_code)} chars) much shorter than initial ({len(initial_code)} chars), using initial code")
                    clean_code = initial_code
                    auto_enhanced = False
                    enhancement_failed = True
                else:
                    auto_enhanced = True
                    print(f"✅ Enhanced code generated: {len(clean_code)} chars")
            except Exception as e:
                print(f"⚠️ Enhancement step failed: {e}")
                print(f"📦 Using initial code as final output")
                clean_code = initial_code
                auto_enhanced = False
                enhancement_failed = True
            
            # Extract monitor data with agent-level scores
            monitor_data = {
                'threshold': 0.75,
                'max_retries': 1,
                'auto_enhanced': auto_enhanced,
                'agent_stats': monitor.monitor_data.get('agent_stats', {}),
                'enhancement_history': monitor.enhancement_history
            }
            
            # Extract features from enhanced monitoring
            enhanced_features = extract_features_from_monitor(monitor.monitor_data)
            
            # Predict enhanced code quality with XGBoost
            if enhancement_failed:
                # Enhancement failed - use initial score
                predicted_score = initial_score
                features = initial_features
                print(f"📊 Enhancement failed - final score: {predicted_score:.3f}")
            else:
                # Enhancement succeeded - predict with XGBoost
                try:
                    # Use global predictor (already loaded)
                    if predictor:
                        predicted_score = predictor.predict(enhanced_features)
                        features = enhanced_features
                        print(f"📊 Enhanced XGBoost score: {predicted_score:.3f}")
                        print(f"📈 Improvement: {predicted_score - initial_score:+.3f}")
                        
                        # CRITICAL: If enhancement made it worse, use initial code!
                        if predicted_score < initial_score:
                            print(f"⚠️ Enhancement made code WORSE! Using initial code instead.")
                            print(f"   Initial score: {initial_score:.3f} > Enhanced score: {predicted_score:.3f}")
                            clean_code = initial_code
                            predicted_score = initial_score
                            features = initial_features
                            auto_enhanced = False
                    else:
                        raise Exception("Predictor not loaded")
                except Exception as e:
                    print(f"⚠️ XGBoost prediction failed: {e}")
                    # Fallback: use max agent score
                    agent_stats = monitor.monitor_data.get('agent_stats', {})
                    agent_scores = []
                    for stats in agent_stats.values():
                        if stats.get('scores'):
                            agent_scores.extend(stats['scores'])
                    predicted_score = max(agent_scores) if agent_scores else initial_score
                    features = enhanced_features
            
            enhancement_loops = 1
        
        # STEP 5: Save to database with BOTH initial and final code
        print(f"📊 Final: Initial={len(initial_code)} chars (score={initial_score:.2f}), Enhanced={len(clean_code)} chars (score={predicted_score:.2f})")
        run_id = db.save_run(
            user_id=user["username"],
            username=user["username"],
            task=request.task,
            code=clean_code,
            predicted_score=float(predicted_score),
            features=features,
            monitor_data=monitor_data,
            initial_code=initial_code,  # Pass initial code
            initial_score=float(initial_score)  # Pass initial score
        )
        
        print(f"✅ Response ready: {len(clean_code)} chars, {predicted_score:.2f} score")
        
        return {
            "run_id": str(run_id),
            "predicted_score": float(predicted_score),
            "initial_score": float(initial_score),
            "code": clean_code,
            "initial_code": initial_code,
            "final_code": clean_code,
            "is_enhancement": is_enhancement,
            "auto_enhanced": auto_enhanced,
            "enhancement_loops": enhancement_loops,
            "features": features,
            "monitor_data": monitor_data,
            "agent_stats": monitor_data.get('agent_stats', {}) if monitor_data else {}
        }
    except Exception as e:
        print(f"ERROR in run_mas: {str(e)}")
        import traceback
        traceback.print_exc()
        raise HTTPException(status_code=500, detail=str(e))

# Alias with hyphen for frontend compatibility
@app.post("/api/run-mas")
async def run_mas_hyphen(request: RunRequest, user = Depends(verify_token)):
    """Alias for /api/run_mas with hyphen instead of underscore"""
    return await run_mas(request, user)


# New: start endpoint that returns initial code immediately and schedules enhancement
@app.post("/api/run-mas-start")
async def run_mas_start(request: RunRequest, background_tasks: BackgroundTasks, user = Depends(verify_token)):
    """Generate initial code quickly and schedule enhancement in background.

    Returns initial code and run_id immediately. Frontend should poll /api/run/{run_id}
    to fetch enhanced results when ready.
    """
    try:
        print(f"[START] MAS start request from {user['username']}: {request.task[:50]}...")
        from AgentMonitor import CodeGenerationMAS, EnhancedAgentMonitor
        from AgentMonitor.gemini_api import gemini_call

        llm = gemini_call

        # Generate initial code fast (no monitoring, FAST MODE always)
        mas_initial = CodeGenerationMAS(llm=llm, language=request.language or 'auto', threshold=1.0, max_retries=0, use_full_mas=False)
        initial_result = await mas_initial.run(request.task, monitor=None)
        if isinstance(initial_result, dict):
            initial_code = initial_result.get('output') or initial_result.get('code') or str(initial_result)
        else:
            initial_code = str(initial_result)

        # Save initial run with placeholder fields
        run_id = db.save_run(user_id=user['username'], username=user['username'], task=request.task,
                             code=initial_code, predicted_score=0.0, features=None, monitor_data=None)

        # Schedule enhancement in background
        lang = (request.language or 'auto').lower()
        background_tasks.add_task(_background_enhance_run, str(run_id), request.task, initial_code, lang, user['username'], request.use_full_mas)

        return {
            'run_id': str(run_id),
            'initial_code': initial_code,
            'message': 'Initial code generated. Enhancement scheduled.'
        }
    except Exception as e:
        print(f"ERROR in run_mas_start: {e}")
        raise HTTPException(status_code=500, detail=str(e))


async def _background_enhance_run(run_id: str, task: str, initial_code: str, language: str, username: str, use_full_mas: bool = False):
    """Background worker: runs enhancement and updates the DB with final code, features, and agent stats."""
    try:
        print(f"[BG] Enhancer started for run {run_id} (FULL MAS: {use_full_mas})")
        from AgentMonitor import CodeGenerationMAS, EnhancedAgentMonitor
        from AgentMonitor.gemini_api import gemini_call
        from AgentMonitor.groq_api import groq_call

        llm = gemini_call
        judge_llm = groq_call

        mas_enhanced = CodeGenerationMAS(llm=llm, language=language, threshold=0.75, max_retries=1, use_full_mas=use_full_mas)
        monitor = EnhancedAgentMonitor(llm=llm, judge_llm=judge_llm, threshold=0.75, max_retries=1, debug=True)  # Enable debug

        # Prepend language directive if requested
        lang_directive = f"LANGUAGE: {language}\n\n" if language and language not in ['auto', 'any'] else ''
        enhancement_task = f"{lang_directive}{task}\n\nExisting code:\n{initial_code}\n\nImprove this code with better quality and best practices."

        print(f"[BG] Running MAS with monitor...")
        enhanced_result = await mas_enhanced.run(enhancement_task, monitor=monitor)

        if isinstance(enhanced_result, dict):
            final_code = enhanced_result.get('output') or enhanced_result.get('code') or str(enhanced_result)
        else:
            final_code = str(enhanced_result)

        print(f"[BG] Enhanced code generated: {len(final_code)} chars")
        print(f"[BG] Monitor data keys: {monitor.monitor_data.keys()}")
        print(f"[BG] Agent stats: {monitor.monitor_data.get('agent_stats', {})}")

        # Extract agent stats and monitor data
        monitor_data = {
            'threshold': monitor.threshold,
            'max_retries': monitor.max_retries,
            'agent_stats': monitor.monitor_data.get('agent_stats', {}),
            'enhancement_history': monitor.enhancement_history,
            'graph_edges': monitor.monitor_data.get('graph_edges', []),
            'conversations': monitor.monitor_data.get('conversations', [])
        }

        # Simple feature extraction from monitor_data
        print(f"[BG] Extracting features from monitor_data...")
        features = extract_features_from_monitor(monitor.monitor_data) if hasattr(monitor, 'monitor_data') else None
        print(f"[BG] Extracted features: {features}")

        # Simple score aggregation
        agent_scores = []
        for a, s in monitor.monitor_data.get('agent_stats', {}).items():
            agent_scores.extend(s.get('scores', []))
        predicted_score = (sum(agent_scores) / len(agent_scores)) if agent_scores else 0.85

        print(f"[BG] Predicted score: {predicted_score}, Agent scores: {agent_scores}")

        # Update run in DB
        db.update_run(run_id, {
            'code': final_code,
            'features': features,
            'monitor_data': monitor_data,
            'predicted_score': float(predicted_score),
            'enhanced_at': datetime.now()
        })

        print(f"[BG] Enhancer finished for run {run_id}, DB updated with {len(features) if features else 0} features")
    except Exception as e:
        import traceback
        print(f"[BG] Enhancer error for run {run_id}: {e}")
        traceback.print_exc()

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

@app.get("/admin/all_runs")
async def get_all_runs_admin():
    """Fetch all runs for admin analytics dashboard - no auth needed for demo"""
    runs = db.get_all_runs()
    for run in runs:
        run["_id"] = str(run["_id"])
    return {"runs": runs, "total": len(runs)}

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
