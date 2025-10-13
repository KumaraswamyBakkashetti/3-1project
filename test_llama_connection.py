"""
Quick test to verify Llama integration with DevTunnel URL
"""
import sys
from pathlib import Path

# Add AgentMonitor to path
sys.path.insert(0, str(Path(__file__).parent / "AgentMonitor"))

from llama import llama_call

print("=" * 70)
print("Testing Llama with DevTunnel URL")
print("=" * 70)

print("\n✓ Testing connection to: https://k7xc1qwz-11434.inc1.devtunnels.ms")
print("✓ Model: qwen3:8b")

try:
    response = llama_call("Write a Python function to add two numbers. Code only.")
    print("\n✅ SUCCESS! Llama is working!")
    print("\nResponse:")
    print("-" * 70)
    print(response)
    print("-" * 70)
    print("\n🎉 System is ready to use with Llama via DevTunnel!")
    print("   This URL works across different networks.")
except Exception as e:
    print(f"\n❌ Error: {e}")
