"""
Debug test to see exactly what's happening with scoring
"""
import asyncio
import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).parent / "AgentMonitor"))

from llama import llama_call
from AgentMonitor import CodeGenerationMAS, EnhancedAgentMonitor

async def debug_test():
    print("=" * 70)
    print("DEBUG: Testing Enhanced Monitor Scoring")
    print("=" * 70)
    
    # Create monitor with debug enabled
    monitor = EnhancedAgentMonitor(
        llm=llama_call,
        threshold=0.7,
        max_retries=1,
        debug=True  # Enable debug
    )
    
    # Test the scoring directly
    print("\n1️⃣ Testing _score_output directly...")
    
    task = "Write a function to add two numbers"
    good_output = "def add(a, b):\n    return a + b"
    
    score = await monitor._score_output(task, good_output, "TestAgent")
    print(f"\n✅ Score returned: {score}")
    print(f"   Expected: > 0.7")
    print(f"   LLM type: {type(monitor.llm)}")
    print(f"   LLM callable: {callable(monitor.llm)}")
    
    # Test with actual agent
    print("\n" + "=" * 70)
    print("2️⃣ Testing with actual MAS agent...")
    print("=" * 70)
    
    mas = CodeGenerationMAS(
        llm=llama_call,
        threshold=0.7,
        max_retries=1
    )
    
    from mas.code_generation_mas import Agent
    
    # Create a test agent
    test_agent = Agent(
        name="TestCoder",
        role="Generate Python code",
        llm=llama_call
    )
    
    task = "Write a Python function to multiply two numbers"
    print(f"\nTask: {task}")
    print("Running agent...")
    
    # Run with monitor
    result = await monitor.run_agent_with_enhancement(
        agent=test_agent,
        task=task,
        agent_name="TestCoder",
        capability="llama"
    )
    
    print(f"\n✅ Result: {result}")
    print(f"   Output length: {len(result.get('output', ''))} chars")
    print(f"   Score: {result.get('score', 0)}")
    print(f"   Enhanced: {result.get('enhanced', False)}")
    
    # Check what was recorded
    if monitor.monitor_data.get("agent_stats", {}).get("TestCoder"):
        stats = monitor.monitor_data["agent_stats"]["TestCoder"]
        print(f"\n📊 Agent Stats:")
        print(f"   Calls: {stats.get('total_calls', 0)}")
        print(f"   Scores: {stats.get('scores', [])}")
        
        convs = stats.get("conversations", [])
        if convs:
            conv = convs[0]
            print(f"\n   First conversation:")
            print(f"   Output: {conv.get('output', '')[:100]}...")
            print(f"   Score: {conv.get('score', 0)}")

asyncio.run(debug_test())
