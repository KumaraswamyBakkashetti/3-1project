"""
Test Llama scoring to see what it returns
"""
import sys
from pathlib import Path
sys.path.insert(0, str(Path(__file__).parent / "AgentMonitor"))

from llama import llama_call

# Test the exact prompt used for scoring
prompt = """You are evaluating an AI agent's output quality.

Task: Write a Python function to calculate factorial of a number

Agent Output:
def factorial(n):
    if n == 0 or n == 1:
        return 1
    result = 1
    for i in range(2, n + 1):
        result *= i
    return result

Rate the output on a scale of 0.0 to 1.0 based on:
1. Correctness: Does it solve the task?
2. Completeness: Are all requirements addressed?
3. Quality: Is it well-structured and clear?

Return ONLY a number between 0.0 and 1.0 (e.g., 0.85)
"""

print("Testing Llama scoring...")
print("=" * 70)

response = llama_call(prompt)
print("Llama Response:")
print(response)
print("=" * 70)

# Try to extract number
import re
match = re.search(r'0?\.\d+|[01]\.?\d*', response)
if match:
    score = float(match.group())
    print(f"\n✅ Extracted score: {score}")
else:
    print("\n❌ Could not extract score!")
