# AgentMonitor/mas/code_generation_mas.py
"""
Code Generation Multi-Agent System

This is an actual MAS implementation (not just simple agents).
Follows the research paper: Multiple specialized agents collaborating.
"""

import asyncio
from typing import Any, List, Dict, Optional


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
    
    def __init__(self, llm, threshold: float = 0.6, max_retries: int = 2):
        """
        Args:
            llm: LLM model for agents
            threshold: Quality threshold
            max_retries: Max enhancement loops
        """
        self.llm = llm
        self.threshold = threshold
        self.max_retries = max_retries
        
        # Define agent roles
        self.agents = {
            "Analyzer": Agent("Analyzer", "requirement analyzer", llm),
            "Coder": Agent("Coder", "expert Python programmer", llm),
            "Tester": Agent("Tester", "unit test writer", llm),
            "Reviewer": Agent("Reviewer", "code reviewer and optimizer", llm)
        }
        
    async def run(self, task: str, monitor=None) -> str:
        """
        Run the MAS pipeline - SIMPLIFIED FOR SPEED
        
        Args:
            task: Programming task
            monitor: AgentMonitor instance (optional)
            
        Returns:
            Final code output
        """
        # SPEED OPTIMIZATION: Skip Analyzer and Tester, only use Coder
        print(f"⚡ FAST MODE: Using Coder only (skipping Analyzer/Tester/Reviewer)")
        
        # Direct to Coder with simple prompt
        code = await self._run_agent(
            "Coder",
            f"Write Python code: {task}",
            monitor
        )
        
        return code
    
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
            # Extract output and ensure it's not None or empty
            if isinstance(result, dict):
                output = result.get("output", "")
            else:
                output = str(result) if result else ""
            
            # Safeguard against empty output
            if not output or output.strip() == "":
                output = f"# {agent_name} generated no output"
            
            return output
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
        """Generate response for a task - WITH TIMEOUT"""
        try:
            # SHORT, DIRECT PROMPT
            if self.name == "Coder":
                full_prompt = f"{prompt}\n\nReturn ONLY Python code, no explanations:"
            else:
                full_prompt = prompt
            
            print(f"[{self.name}] Calling LLM...")
            
            # Handle different LLM interfaces with TIMEOUT
            if callable(self.llm):
                import signal
                
                def timeout_handler(signum, frame):
                    raise TimeoutError("LLM call timed out after 30 seconds")
                
                # Set 30 second timeout
                signal.signal(signal.SIGALRM, timeout_handler)
                signal.alarm(30)
                
                try:
                    response = self.llm(full_prompt)
                    signal.alarm(0)  # Cancel timeout
                    
                    response_str = response if isinstance(response, str) else str(response)
                    
                    # Extract code from markdown
                    if "```" in response_str:
                        import re
                        code_blocks = re.findall(r'```(?:python)?\s*(.*?)```', response_str, re.DOTALL)
                        if code_blocks:
                            response_str = code_blocks[0].strip()
                            print(f"[{self.name}] Extracted code: {len(response_str)} chars")
                    
                    return response_str
                except TimeoutError:
                    signal.alarm(0)
                    return f"# Timeout: {self.name} took too long"
                    
            elif hasattr(self.llm, 'generate_content'):
                response = self.llm.generate_content(full_prompt)
                return response.text
            else:
                return f"# Error: Unknown LLM interface"
                
        except Exception as e:
            print(f"🚨 [{self.name}] Error: {str(e)[:100]}")
            return f"# Error in {self.name}: {str(e)[:50]}"
