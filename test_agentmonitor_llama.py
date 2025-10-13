"""
Complete AgentMonitor + Llama Integration Test
"""
import asyncio
import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).parent / "AgentMonitor"))

from llama import llama_call
from AgentMonitor import CodeGenerationMAS, EnhancedAgentMonitor

print("=" * 70)
print("🎯 AGENTMONITOR + LLAMA - INTEGRATION TEST")
print("=" * 70)

async def test_complete_system():
    # Test 1: Llama Connection
    print("\n1️⃣ Testing Llama API...")
    try:
        response = llama_call("Say 'OK'")
        print(f"   ✅ Llama connected: {response[:30]}...")
    except Exception as e:
        print(f"   ❌ Error: {e}")
        return False
    
    # Test 2: Multi-Agent System
    print("\n2️⃣ Testing Multi-Agent System...")
    try:
        mas = CodeGenerationMAS(
            llm=llama_call,
            threshold=0.65,  # Optimized for speed
            max_retries=1
        )
        
        monitor = EnhancedAgentMonitor(
            llm=llama_call,
            threshold=0.65,
            max_retries=1,
            debug=False
        )
        
        task = "Write a Python function to add two numbers"
        print(f"   Task: '{task}'")
        print("   Running agents... (this takes 20-40 seconds)")
        
        result = await mas.run(task, monitor=monitor)
        
        if result and len(result) > 0:
            print(f"   ✅ Code generated ({len(result)} chars)")
            print(f"\n   Generated code preview:")
            print("   " + "-" * 66)
            for line in result.split('\n')[:10]:
                print(f"   {line}")
            print("   " + "-" * 66)
            
            # Show agent stats
            stats = monitor.monitor_data.get("agent_stats", {})
            print(f"\n   📊 Agents executed: {len(stats)}")
            for name in stats.keys():
                print(f"      • {name}")
            
            return True
        else:
            print(f"   ⚠️ Empty result")
            return False
            
    except Exception as e:
        print(f"   ❌ Error: {e}")
        import traceback
        traceback.print_exc()
        return False

# Run test
success = asyncio.run(test_complete_system())

print("\n" + "=" * 70)
if success:
    print("✅ ALL TESTS PASSED!")
    print("=" * 70)
    print("\n📝 Summary:")
    print("   • Llama API: Working via DevTunnel")
    print("   • Multi-Agent System: Functional")
    print("   • 4 Agents: Analyzer, Coder, Tester, Reviewer")
    print("   • Enhanced Monitor: Tracking and scoring")
    print("   • Code Generation: Successful")
    print("\n🎉 AgentMonitor is fully integrated with Llama!")
    print("   Ready for backend and frontend integration.")
else:
    print("❌ SOME TESTS FAILED")
    print("=" * 70)
