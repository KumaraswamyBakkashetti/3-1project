"""
Debug: See what the agents are actually generating
"""
import asyncio
import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).parent / "AgentMonitor"))

from llama import llama_call
from AgentMonitor import CodeGenerationMAS, EnhancedAgentMonitor

async def debug_agent_outputs():
    print("=" * 70)
    print("DEBUG: What are agents actually generating?")
    print("=" * 70)
    
    task = "Write a Python function to calculate factorial of a number"
    
    # Test each agent individually
    from AgentMonitor.mas.code_generation_mas import Agent
    
    agents = [
        Agent("Analyzer", "Analyze the requirements and break them down", llama_call),
        Agent("Coder", "Write clean, efficient Python code", llama_call),
        Agent("Tester", "Create unit tests for the code", llama_call),
        Agent("Reviewer", "Review code quality and suggest improvements", llama_call)
    ]
    
    for agent in agents:
        print(f"\n{'=' * 70}")
        print(f"🤖 {agent.name}")
        print('=' * 70)
        print(f"Task: {task}\n")
        
        output = agent.generate_response(task)
        print(f"Output ({len(output)} chars):")
        print("-" * 70)
        print(output[:500])  # First 500 chars
        print("-" * 70)
        
        # Now score it
        monitor = EnhancedAgentMonitor(llm=llama_call, threshold=0.7, max_retries=1)
        score = await monitor._score_output(task, output, agent.name)
        print(f"\n📊 Score: {score}")
        
        if score < 0.7:
            print(f"⚠️ LOW SCORE! Why?")
            if "Error:" in output:
                print("   - Output contains error")
            if len(output) < 50:
                print("   - Output too short")
            if "provide" in output.lower() and "code" in output.lower():
                print("   - Agent asking for code instead of generating it!")

asyncio.run(debug_agent_outputs())
