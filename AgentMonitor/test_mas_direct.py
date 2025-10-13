"""
Direct test of MAS code generation to debug null output issue
"""
import asyncio
import sys
from pathlib import Path

# Add AgentMonitor to path
sys.path.insert(0, str(Path(__file__).parent))

from gemini_api import gemini_call
from mas.code_generation_mas import CodeGenerationMAS
from core.enhanced_monitor import EnhancedAgentMonitor


async def test_mas():
    """Test MAS code generation directly"""
    
    print("=" * 80)
    print("🧪 DIRECT MAS TEST - Checking for null output bug")
    print("=" * 80)
    
    # Simple test task
    task = "Write a Python function to calculate factorial of a number"
    
    print(f"\n📝 Task: {task}")
    print(f"\n🔧 LLM Type: {type(gemini_call)}")
    print(f"🔧 LLM Callable: {callable(gemini_call)}")
    
    # Test 1: Direct LLM call
    print("\n" + "=" * 80)
    print("TEST 1: Direct LLM Call")
    print("=" * 80)
    
    try:
        direct_response = gemini_call("Write a hello world function in Python")
        print(f"✅ Direct LLM Response ({len(direct_response)} chars):")
        print(direct_response[:200])
    except Exception as e:
        print(f"❌ Direct LLM call failed: {e}")
        return
    
    # Test 2: MAS without monitor
    print("\n" + "=" * 80)
    print("TEST 2: MAS Without Monitor")
    print("=" * 80)
    
    try:
        mas_simple = CodeGenerationMAS(
            llm=gemini_call,
            threshold=0.7,
            max_retries=1
        )
        
        result_no_monitor = await mas_simple.run(task, monitor=None)
        print(f"\n✅ MAS Result (no monitor): {type(result_no_monitor)}")
        print(f"📏 Length: {len(result_no_monitor) if result_no_monitor else 0} chars")
        print(f"📄 Preview:\n{result_no_monitor[:300] if result_no_monitor else 'NULL/EMPTY'}")
        
    except Exception as e:
        print(f"❌ MAS without monitor failed: {e}")
        import traceback
        traceback.print_exc()
    
    # Test 3: MAS with monitor
    print("\n" + "=" * 80)
    print("TEST 3: MAS With Monitor")
    print("=" * 80)
    
    try:
        mas = CodeGenerationMAS(
            llm=gemini_call,
            threshold=0.7,
            max_retries=1
        )
        
        monitor = EnhancedAgentMonitor(
            llm=gemini_call,
            threshold=0.7,
            max_retries=1,
            debug=True  # Enable debug output
        )
        
        print("\n🚀 Running MAS with monitor...")
        result = await mas.run(task, monitor=monitor)
        
        print("\n" + "=" * 80)
        print("RESULTS")
        print("=" * 80)
        
        print(f"\n✅ MAS Result Type: {type(result)}")
        print(f"📏 Length: {len(result) if result else 0} chars")
        
        if result:
            print(f"\n📄 Full Result:\n{result}")
        else:
            print("\n❌ RESULT IS NULL/EMPTY!")
        
        # Check monitor data
        print("\n" + "=" * 80)
        print("MONITOR DATA")
        print("=" * 80)
        
        for agent_name, stats in monitor.monitor_data.get("agent_stats", {}).items():
            print(f"\n🤖 Agent: {agent_name}")
            print(f"   Total calls: {stats.get('total_calls', 0)}")
            print(f"   Enhancement triggered: {stats.get('enhancement_triggered', 0)}")
            print(f"   Scores: {stats.get('scores', [])}")
            
            conversations = stats.get("conversations", [])
            if conversations:
                last_conv = conversations[-1]
                output = last_conv.get("output", "")
                print(f"   Last output length: {len(output)} chars")
                print(f"   Last output preview: {output[:200]}")
                print(f"   Last score: {last_conv.get('score', 0)}")
            else:
                print("   ⚠️ No conversations recorded!")
        
    except Exception as e:
        print(f"\n❌ MAS with monitor failed: {e}")
        import traceback
        traceback.print_exc()
    
    print("\n" + "=" * 80)
    print("TEST COMPLETE")
    print("=" * 80)


if __name__ == "__main__":
    asyncio.run(test_mas())
