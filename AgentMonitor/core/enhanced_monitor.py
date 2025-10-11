# AgentMonitor/core/enhanced_monitor.py
"""
COMPLETE AgentMonitor with Enhancement Loops
Combines research paper methodology + production-ready features
"""

import asyncio
import json
import time
import os
from typing import Any, Callable, Dict, List, Optional, Tuple
from datetime import datetime
from pathlib import Path
import google.generativeai as genai


class EnhancedAgentMonitor:
    """
    Production-ready AgentMonitor with:
    1. Non-invasive monitoring (paper approach)
    2. Enhancement loops (retry if score < threshold)
    3. 16 feature extraction
    4. XGBoost prediction
    
    Usage:
        monitor = EnhancedAgentMonitor(
            api_key="your_key",
            threshold=0.6,  # Retry if score < 0.6
            max_retries=2
        )
        
        # Monitor agents with auto-enhancement
        result = await monitor.run_agent_with_enhancement(
            agent=my_agent,
            task="Write a function...",
            agent_name="Coder"
        )
    """
    
    def __init__(
        self,
        api_key: Optional[str] = None,
        threshold: float = 0.6,
        max_retries: int = 2,
        log_dir: str = "logs",
        debug: bool = False
    ):
        """
        Args:
            api_key: Gemini API key for LLM scoring
            threshold: Score threshold for enhancement (0-1)
            max_retries: Max enhancement attempts
            log_dir: Directory for logs
            debug: Enable debug output
        """
        self.threshold = threshold
        self.max_retries = max_retries
        self.log_dir = Path(log_dir)
        self.log_dir.mkdir(exist_ok=True)
        self.debug = debug
        
        # Initialize LLM for scoring
        if api_key:
            genai.configure(api_key=api_key)
            self.llm = genai.GenerativeModel("models/gemini-2.0-flash")  # FIXED: Using available model
        else:
            self.llm = None
            if debug:
                print("[WARNING] No API key - LLM scoring disabled")
        
        # Monitoring data (follows paper structure)
        self.monitor_data = {
            "conversations": [],      # All agent interactions
            "agent_stats": {},        # Per-agent statistics
            "graph_edges": [],        # Conversation graph
            "metadata": {
                "start_time": datetime.now().isoformat(),
                "threshold": threshold,
                "max_retries": max_retries
            }
        }
        
        # Enhancement tracking
        self.enhancement_history = []
        
    async def run_agent_with_enhancement(
        self,
        agent: Any,
        task: str,
        agent_name: str,
        capability: str = "gemini",
        context: Optional[Dict] = None
    ) -> Dict[str, Any]:
        """
        Run agent with automatic enhancement loops.
        
        This is the MAIN method that combines:
        - Monitoring (record I/O)
        - LLM scoring (quality assessment)
        - Enhancement loops (retry if low score)
        
        Args:
            agent: Agent object with run() or generate() method
            task: Task/prompt for agent
            agent_name: Agent identifier
            capability: LLM capability (for feature extraction)
            context: Optional context from previous agents
            
        Returns:
            Dict with:
                - output: Final agent output
                - score: Final quality score
                - attempts: Number of enhancement loops
                - enhanced: Whether enhancement was triggered
        """
        if agent_name not in self.monitor_data["agent_stats"]:
            self._initialize_agent_stats(agent_name, capability)
        
        attempts = 0
        best_output = None
        best_score = 0.0
        enhanced = False
        
        while attempts <= self.max_retries:
            # Run agent
            start_time = time.time()
            
            try:
                # Try different agent interfaces
                if hasattr(agent, 'run'):
                    if asyncio.iscoroutinefunction(agent.run):
                        output = await agent.run(task)
                    else:
                        output = agent.run(task)
                elif hasattr(agent, 'generate'):
                    output = agent.generate(task)
                elif hasattr(agent, 'generate_response'):
                    output = agent.generate_response(task)
                elif callable(agent):
                    output = agent(task)
                else:
                    raise ValueError(f"Agent {agent_name} has no run/generate method")
                    
            except Exception as e:
                print(f"[ERROR] Agent {agent_name} failed: {e}")
                output = f"ERROR: {str(e)}"
                
            latency = time.time() - start_time
            
            # Extract output string
            if isinstance(output, dict):
                output_str = output.get('output', output.get('response', str(output)))
            else:
                output_str = str(output)
            
            # Score output
            score = await self._score_output(task, output_str, agent_name)
            
            # Record conversation
            self._record_conversation(
                agent_name=agent_name,
                input_text=task,
                output_text=output_str,
                score=score,
                latency=latency,
                attempt=attempts
            )
            
            # Update best output
            if score > best_score:
                best_output = output_str
                best_score = score
            
            # Check if enhancement needed
            if score >= self.threshold:
                # Good enough - accept
                if self.debug:
                    print(f"[{agent_name}] ✅ Score {score:.2f} >= {self.threshold:.2f} (attempt {attempts})")
                break
            else:
                # Try enhancement
                if attempts < self.max_retries:
                    enhanced = True
                    attempts += 1
                    
                    # Generate enhancement feedback
                    feedback = await self._generate_enhancement_feedback(
                        task, output_str, score
                    )
                    
                    # Modify task with feedback for next attempt
                    task = f"{task}\n\nPrevious attempt scored {score:.2f}/1.0. Feedback:\n{feedback}\n\nPlease improve the response."
                    
                    if self.debug:
                        print(f"[{agent_name}] ⚠️ Score {score:.2f} < {self.threshold:.2f} - Retry {attempts}/{self.max_retries}")
                    
                    # Track enhancement
                    self.enhancement_history.append({
                        "agent": agent_name,
                        "attempt": attempts,
                        "score": score,
                        "feedback": feedback
                    })
                else:
                    # Max retries reached
                    if self.debug:
                        print(f"[{agent_name}] ❌ Max retries reached. Best score: {best_score:.2f}")
                    break
        
        # Update agent stats
        self.monitor_data["agent_stats"][agent_name]["total_calls"] += 1
        self.monitor_data["agent_stats"][agent_name]["enhancement_triggered"] += (1 if enhanced else 0)
        self.monitor_data["agent_stats"][agent_name]["scores"].append(best_score)
        
        return {
            "output": best_output,
            "score": best_score,
            "attempts": attempts,
            "enhanced": enhanced,
            "agent_name": agent_name
        }
    
    async def _score_output(
        self,
        task: str,
        output: str,
        agent_name: str
    ) -> float:
        """
        Score agent output using LLM (0-1 scale).
        
        Follows paper's "personal score" methodology.
        """
        if not self.llm:
            # Fallback: heuristic scoring
            return self._heuristic_score(output)
        
        try:
            prompt = f"""You are evaluating an AI agent's output quality.

Task: {task}

Agent Output:
{output}

Rate the output on a scale of 0.0 to 1.0 based on:
1. Correctness: Does it solve the task?
2. Completeness: Are all requirements addressed?
3. Quality: Is it well-structured and clear?

Return ONLY a number between 0.0 and 1.0 (e.g., 0.85)
"""
            
            response = self.llm.generate_content(prompt)
            score_text = response.text.strip()
            
            # Extract number
            import re
            match = re.search(r'0?\.\d+|[01]\.?\d*', score_text)
            if match:
                score = float(match.group())
                return max(0.0, min(1.0, score))
            else:
                return self._heuristic_score(output)
                
        except Exception as e:
            if self.debug:
                print(f"[WARNING] LLM scoring failed: {e}")
            return self._heuristic_score(output)
    
    def _heuristic_score(self, output: str) -> float:
        """Fallback heuristic scoring."""
        if not output or "Error:" in output:
            return 0.3
        if len(output) < 50:
            return 0.5
        if len(output) > 200:
            return 0.75
        return 0.6  # Default score for medium-length outputs
    
    async def _generate_enhancement_feedback(
        self,
        task: str,
        output: str,
        score: float
    ) -> str:
        """Generate feedback for enhancement."""
        if not self.llm:
            return f"Score {score:.2f} is below threshold. Please provide a more complete and accurate response."
        
        try:
            prompt = f"""The agent's output scored {score:.2f}/1.0, which is below the quality threshold.

Task: {task}

Current Output:
{output}

Provide brief, actionable feedback (2-3 sentences) on how to improve this output to meet the requirements better.
"""
            
            response = self.llm.generate_content(prompt)
            return response.text.strip()
            
        except Exception:
            return f"Score {score:.2f} is below threshold. Please provide more detail and ensure correctness."
    
    def _initialize_agent_stats(self, agent_name: str, capability: str):
        """Initialize statistics for a new agent."""
        self.monitor_data["agent_stats"][agent_name] = {
            "capability": capability,
            "total_calls": 0,
            "enhancement_triggered": 0,
            "scores": [],
            "latencies": [],
            "token_usage": 0
        }
    
    def _record_conversation(
        self,
        agent_name: str,
        input_text: str,
        output_text: str,
        score: float,
        latency: float,
        attempt: int
    ):
        """Record conversation in monitoring data."""
        step = len(self.monitor_data["conversations"])
        
        self.monitor_data["conversations"].append({
            "step": step,
            "agent": agent_name,
            "input": input_text[:500],  # Truncate for storage
            "output": output_text[:500],
            "score": score,
            "latency": latency,
            "attempt": attempt,
            "timestamp": datetime.now().isoformat()
        })
        
        # Update agent stats
        self.monitor_data["agent_stats"][agent_name]["latencies"].append(latency)
        
        # Estimate tokens (rough approximation)
        tokens = (len(input_text) + len(output_text)) // 4
        self.monitor_data["agent_stats"][agent_name]["token_usage"] += tokens
    
    def record_graph_edge(self, from_agent: str, to_agent: str):
        """
        Record edge in conversation graph.
        
        Call this when one agent's output becomes another's input.
        """
        self.monitor_data["graph_edges"].append([from_agent, to_agent])
        
        if self.debug:
            print(f"[GRAPH] {from_agent} → {to_agent}")
    
    def save(self, filepath: str = "monitor_output.json"):
        """Save monitoring data to JSON."""
        filepath = Path(filepath)
        filepath.parent.mkdir(parents=True, exist_ok=True)
        
        # Add summary statistics
        self.monitor_data["metadata"]["end_time"] = datetime.now().isoformat()
        self.monitor_data["metadata"]["total_agents"] = len(self.monitor_data["agent_stats"])
        self.monitor_data["metadata"]["total_conversations"] = len(self.monitor_data["conversations"])
        self.monitor_data["metadata"]["total_enhancements"] = len(self.enhancement_history)
        
        with open(filepath, 'w') as f:
            json.dump(self.monitor_data, f, indent=2)
        
        print(f"[SAVED] Monitoring data saved to {filepath}")
    
    def load(self, filepath: str):
        """Load monitoring data from JSON."""
        with open(filepath, 'r') as f:
            self.monitor_data = json.load(f)
        
        print(f"[LOADED] Monitoring data loaded from {filepath}")
    
    def get_summary(self) -> Dict[str, Any]:
        """Get summary statistics."""
        summary = {
            "total_agents": len(self.monitor_data["agent_stats"]),
            "total_conversations": len(self.monitor_data["conversations"]),
            "total_enhancements": len(self.enhancement_history),
            "agents": {}
        }
        
        for agent_name, stats in self.monitor_data["agent_stats"].items():
            scores = stats.get("scores", [])
            latencies = stats.get("latencies", [])
            
            summary["agents"][agent_name] = {
                "calls": stats["total_calls"],
                "enhancements": stats["enhancement_triggered"],
                "avg_score": sum(scores) / len(scores) if scores else 0.0,
                "min_score": min(scores) if scores else 0.0,
                "avg_latency": sum(latencies) / len(latencies) if latencies else 0.0,
                "token_usage": stats.get("token_usage", 0)
            }
        
        return summary
    
    def print_summary(self):
        """Print formatted summary."""
        summary = self.get_summary()
        
        print("\n" + "=" * 60)
        print("AGENT MONITOR SUMMARY")
        print("=" * 60)
        print(f"Total Agents: {summary['total_agents']}")
        print(f"Total Conversations: {summary['total_conversations']}")
        print(f"Total Enhancements: {summary['total_enhancements']}")
        print("\nPer-Agent Statistics:")
        print("-" * 60)
        
        for agent_name, stats in summary["agents"].items():
            print(f"\n{agent_name}:")
            print(f"  Calls:        {stats['calls']}")
            print(f"  Enhancements: {stats['enhancements']}")
            print(f"  Avg Score:    {stats['avg_score']:.3f}")
            print(f"  Min Score:    {stats['min_score']:.3f}")
            print(f"  Avg Latency:  {stats['avg_latency']:.3f}s")
            print(f"  Tokens:       {stats['token_usage']}")
        
        print("\n" + "=" * 60 + "\n")
