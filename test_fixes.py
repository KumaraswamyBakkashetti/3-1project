"""
Test if collective_score issue is fixed
"""
import os
from dotenv import load_dotenv
from Agent_Monitor.run_with_monitor import run_prompt

load_dotenv()

print("=" * 70)
print("🧪 TESTING COLLECTIVE SCORE FIX")
print("=" * 70)

api_key = os.getenv("GEMINI_API_KEY")

# Run a simple task
prompt = "Write Python code to calculate factorial of a number"
print(f"\nPrompt: {prompt}")
print("\nRunning...")

data, features, log, summary = run_prompt(
    prompt, 
    task_type="code", 
    api_key=api_key,
    threshold=0.6,  # Lowered threshold
    max_retries=2
)

print("\n" + "=" * 70)
print("📊 RESULTS")
print("=" * 70)

print(f"\n✓ Collective Score: {features.get('collective_score', 'N/A')}")
print(f"  Expected: NOT 0.5 (should vary)")
print(f"  Actual: {'PASS ✅' if features.get('collective_score') != 0.5 else 'FAIL ❌ Still 0.5'}")

print(f"\n✓ Max Loops: {features.get('max_loops', 'N/A')}")
print(f"  Expected: 0, 1, or 2 (should vary)")
print(f"  Actual: {'PASS ✅' if features.get('max_loops') in [0, 1] else 'MIGHT STILL HIT MAX'}")

print(f"\n✓ Avg Personal Score: {features.get('avg_personal_score', 'N/A'):.3f}")
print(f"  With threshold=0.6, scores > 0.6 should not need enhancement")

print(f"\n✓ Min Personal Score: {features.get('min_personal_score', 'N/A'):.3f}")

print("\n" + "=" * 70)
print("💡 EXPLANATION")
print("=" * 70)

if features.get('collective_score') == 0.5:
    print("\n❌ Collective score is still 0.5!")
    print("   Check console output above for:")
    print("   [WARNING] No LLM client provided for collective score")
    print("\n   This means llm_client is not being passed correctly.")
else:
    print(f"\n✅ Collective score is {features.get('collective_score'):.3f}")
    print("   LLM is working! The fix worked!")

if features.get('max_loops') < 2:
    print(f"\n✅ Max loops is {features.get('max_loops')} (not hitting max!)")
    print("   Lowered threshold (0.6) is working!")
elif features.get('avg_personal_score', 0) > 0.6:
    print(f"\n✅ Avg score {features.get('avg_personal_score'):.3f} > 0.6")
    print("   But max_loops=2 means some agents still needed enhancement")
else:
    print(f"\n⚠️  Avg score {features.get('avg_personal_score', 0):.3f} < 0.6")
    print("   That's why all agents hit max_loops=2")
    print("   Consider lowering threshold further to 0.5")

print("\n" + "=" * 70)
