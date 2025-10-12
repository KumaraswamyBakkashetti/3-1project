# AgentMonitor/mas/code_generation_mas.py
"""
Code Generation Multi-Agent System

This is an actual MAS implementation (not just simple agents).
Follows the research paper: Multiple specialized agents collaborating.
"""

import asyncio
from typing import Any, List, Dict, Optional
from llama import llama_call


class CodeGenerationMAS:
    """
    Multi-Agent System for code generation tasks.
    
    Agents:
    1. Analyzer: Analyzes requirements
    2. Coder: Writes code
    3. Tester: Creates tests
    4. Reviewer: Reviews and improves
    
    Flow: Analyzer → Coder → Tester → Reviewer
    """
    
    def __init__(self, llm, threshold: float = 0.6, max_retries: int = 2, skip_tester: bool = False):
        """
        Args:
            llm: LLM model for agents
            threshold: Quality threshold
            max_retries: Max enhancement loops
            skip_tester: If True, skip tester (3-agent pipeline for variance)
        """
        self.llm = llm
        self.threshold = threshold
        self.max_retries = max_retries
        self.skip_tester = skip_tester
        
        # Define agent roles
        self.agents = {
            "Analyzer": Agent("Analyzer", "requirement analyzer", llm),
            "Coder": Agent("Coder", "expert Python programmer", llm),
            "Tester": Agent("Tester", "unit test writer", llm),
            "Reviewer": Agent("Reviewer", "code reviewer and optimizer", llm)
        }
        
    async def run(self, task: str, monitor=None) -> str:
        """
        Run the MAS pipeline on a task.
        
        Args:
            task: Programming task (e.g., "Write a function to sort a list")
            monitor: AgentMonitor instance (optional)
            
        Returns:
            Final code output
        """
        # Step 1: Analyzer
        analysis = await self._run_agent(
            "Analyzer",
            f"Analyze this programming task and break it down:\n{task}",
            monitor
        )
        
        # Record graph edge: Analyzer → Coder
        if monitor:
            monitor.record_graph_edge("Analyzer", "Coder")
        
        # Step 2: Coder
        code = await self._run_agent(
            "Coder",
            f"Requirements: {analysis}\n\nWrite Python code to solve: {task}",
            monitor
        )
        
        # Step 3: Tester (optional - skip for variance)
        if not self.skip_tester:
            # Record graph edge: Coder → Tester
            if monitor:
                monitor.record_graph_edge("Coder", "Tester")
            
            tests = await self._run_agent(
                "Tester",
                f"Code:\n{code}\n\nWrite unit tests for this code.",
                monitor
            )
            
            # Record graph edge: Tester → Reviewer
            if monitor:
                monitor.record_graph_edge("Tester", "Reviewer")
            
            # Step 4: Reviewer
            final = await self._run_agent(
                "Reviewer",
                f"Code:\n{code}\n\nTests:\n{tests}\n\nReview and improve the code.",
                monitor
            )
        else:
            # Skip tester, go directly to reviewer (3-agent pipeline)
            # Record graph edge: Coder → Reviewer
            if monitor:
                monitor.record_graph_edge("Coder", "Reviewer")
            
            # Step 4: Reviewer (without tests)
            final = await self._run_agent(
                "Reviewer",
                f"Code:\n{code}\n\nReview and improve the code.",
                monitor
            )
        
        # Add feedback edge: Reviewer → Analyzer (creates triangles for clustering)
        # This simulates Reviewer providing feedback to Analyzer for next iteration
        if monitor:
            monitor.record_graph_edge("Reviewer", "Analyzer")
        
        return final
    
    async def _run_agent(self, agent_name: str, task: str, monitor=None) -> str:
        """Run single agent with optional monitoring"""
        agent = self.agents[agent_name]
        
        if monitor:
            # Use monitor's run_agent_with_enhancement
            result = await monitor.run_agent_with_enhancement(
                agent=agent,
                task=task,
                agent_name=agent_name,
                capability="llama"
            )
            return result.get("output", "") if isinstance(result, dict) else str(result)
        else:
            # Direct execution
            return agent.generate_response(task)


class Agent:
    """Individual agent within the MAS"""
    
    def __init__(self, name: str, role: str, llm):
        self.name = name
        self.role = role
        self.llm = llm
    
    def generate_response(self, prompt: str) -> str:
        """Generate response for a task"""
        try:
            full_prompt = f"You are a {self.role}. {prompt}"
            # Use llama_call helper directly
            response = llama_call(full_prompt)
            return response
        except Exception as e:
            return f"Error: {str(e)}"
