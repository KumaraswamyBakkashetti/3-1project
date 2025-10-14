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
        
        # Step 2: Coder
        code = await self._run_agent(
            "Coder",
            f"Requirements: {analysis}\n\nWrite Python code to solve: {task}",
            monitor
        )
        
        # Step 3: Tester
        tests = await self._run_agent(
            "Tester",
            f"Code:\n{code}\n\nWrite unit tests for this code.",
            monitor
        )
        
        # Step 4: Reviewer
        final = await self._run_agent(
            "Reviewer",
            f"Code:\n{code}\n\nTests:\n{tests}\n\nReview and improve the code.",
            monitor
        )
        
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
        """Generate response for a task"""
        try:
            # Optimize prompts for code-only output (no explanations)
            if self.name == "Coder":
                full_prompt = f"You are a {self.role}. {prompt}\n\nRULE: Output must be PURE EXECUTABLE PYTHON CODE ONLY. No markdown, no explanations, no text before or after. Start directly with 'def' or 'import'."
            elif self.name == "Reviewer":
                full_prompt = f"You are a {self.role}. {prompt}\n\nRULE: Output must be PURE EXECUTABLE PYTHON CODE ONLY. No markdown, no explanations, no text before or after."
            else:
                full_prompt = f"You are a {self.role}. {prompt}"
            
            # Handle different LLM interfaces
            if callable(self.llm):
                # Function interface (like gemini_call)
                response = self.llm(full_prompt)
                response_str = response if isinstance(response, str) else str(response)
                
                # Extract code from markdown if present (Gemini often wraps in ```)
                if "```" in response_str:
                    import re
                    # Find all code blocks
                    code_blocks = re.findall(r'```(.*?)```', response_str, re.DOTALL)
                    if code_blocks:
                        # Take first code block and remove "python" keyword if present
                        code = code_blocks[0].strip()
                        if code.startswith('python'):
                            code = code[6:].strip()  # Remove "python" + newline
                        if code:  # Make sure we got something
                            response_str = code
                            print(f"[{self.name}] Extracted {len(code)} chars of code from markdown")
                
                return response_str
            elif hasattr(self.llm, 'generate_content'):
                # Model object interface (like Gemini model)
                response = self.llm.generate_content(full_prompt)
                return response.text
            else:
                return f"Error: LLM has unknown interface"
                
        except Exception as e:
            error_msg = f"Error in {self.name}: {str(e)}"
            print(f"🚨 {error_msg}")
            return error_msg
