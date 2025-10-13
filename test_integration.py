"""
Final integration test - Llama with Backend
"""
import requests
import sys
from pathlib import Path

# Add AgentMonitor to path
sys.path.insert(0, str(Path(__file__).parent / "AgentMonitor"))

print("=" * 70)
print("LLAMA INTEGRATION - FINAL TEST")
print("=" * 70)

# Test 1: Direct Llama call
print("\n1️⃣ Testing direct Llama call...")
try:
    from llama import llama_call
    response = llama_call("Write a Python function to multiply two numbers. Code only, no explanation.")
    print(f"✅ Llama working!")
    print(f"Response preview: {response[:80]}...")
except Exception as e:
    print(f"❌ Error: {e}")
    sys.exit(1)

# Test 2: Backend API
print("\n2️⃣ Testing backend API...")
API_URL = "http://localhost:8080"

try:
    # Login
    response = requests.post(
        f"{API_URL}/api/login",
        json={"username": "admin", "password": "admin123"},
        timeout=10
    )
    if response.status_code == 200:
        token = response.json()["token"]
        print("✅ Backend API responding")
        print(f"✅ Login successful")
    else:
        print(f"❌ Login failed: {response.status_code}")
        sys.exit(1)
except Exception as e:
    print(f"❌ Backend not accessible: {e}")
    print("   Make sure backend is running: cd backend && python app.py")
    sys.exit(1)

print("\n" + "=" * 70)
print("✅ SYSTEM READY!")
print("=" * 70)
print("\n📋 Configuration:")
print("   • LLM: Llama via Ollama")
print("   • Server: https://k7xc1qwz-11434.inc1.devtunnels.ms")
print("   • Model: qwen3:8b")
print("   • Backend: http://localhost:8080")
print("   • Frontend: http://localhost:3000")
print("\n🎯 Optimizations for speed:")
print("   • Lower threshold (0.65) for faster completion")
print("   • Reduced retries (1 instead of 2-3)")
print("   • Token limit (512 instead of 2048)")
print("   • Temperature (0.3 for focused responses)")
print("\n✅ System is fully integrated and ready to use!")
