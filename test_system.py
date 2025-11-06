"""
Test AgentMonitor complete workflow to identify issues
"""
import requests
import json
import time

BASE_URL = "http://localhost:8080"

print("="*70)
print("AGENTMONITOR SYSTEM TEST")
print("="*70)

# Test 1: Health Check
print("\n[1/5] Testing Health Endpoint...")
try:
    r = requests.get(f"{BASE_URL}/api/health", timeout=10)
    print(f"✅ Health check: {r.status_code}")
    print(f"   Response: {r.json()}")
except Exception as e:
    print(f"❌ Health check failed: {e}")
    exit(1)

# Test 2: Register User
print("\n[2/5] Testing User Registration...")
test_user = f"testuser_{int(time.time())}"
test_pass = "testpass123"

try:
    r = requests.post(
        f"{BASE_URL}/api/register",
        json={"username": test_user, "password": test_pass},
        timeout=10
    )
    if r.status_code == 201:
        print(f"✅ User registered: {test_user}")
    elif r.status_code == 400 and "already exists" in r.text:
        print(f"⚠️  User already exists, continuing...")
    else:
        print(f"❌ Registration failed: {r.status_code} - {r.text}")
except Exception as e:
    print(f"❌ Registration error: {e}")

# Test 3: Login
print("\n[3/5] Testing Login...")
try:
    r = requests.post(
        f"{BASE_URL}/api/login",
        json={"username": test_user, "password": test_pass},
        timeout=10
    )
    if r.status_code == 200:
        token = r.json()['token']
        print(f"✅ Login successful")
        print(f"   Token: {token[:50]}...")
    else:
        print(f"❌ Login failed: {r.status_code} - {r.text}")
        exit(1)
except Exception as e:
    print(f"❌ Login error: {e}")
    exit(1)

# Test 4: Simple Code Generation (run-mas-start)
print("\n[4/5] Testing Simple Code Generation...")
print("   Task: 'Write a function to add two numbers'")
print("   This should be FAST (~10-15 seconds)...")

try:
    start_time = time.time()
    r = requests.post(
        f"{BASE_URL}/api/run-mas-start",
        json={
            "task": "Write a Python function to add two numbers",
            "language": "python",
            "use_full_mas": False
        },
        headers={"Authorization": f"Bearer {token}"},
        timeout=60  # 60 second timeout
    )
    elapsed = time.time() - start_time
    
    if r.status_code == 200:
        result = r.json()
        print(f"✅ Code generated in {elapsed:.1f}s")
        print(f"   Run ID: {result.get('run_id', 'N/A')}")
        
        # predicted_score might not be in response for /api/run-mas-start
        score = result.get('predicted_score', None)
        if score is not None:
            print(f"   Initial Score: {score:.3f}")
        
        print(f"\n   Generated Code Preview:")
        code = result.get('initial_code', '')
        print("   " + "\n   ".join(code[:200].split('\n')))
        if len(code) > 200:
            print(f"   ... ({len(code)} chars total)")
    else:
        print(f"❌ Code generation failed: {r.status_code}")
        print(f"   Response: {r.text[:500]}")
        
except requests.Timeout:
    print(f"❌ Request timed out after 60 seconds")
    print("   Possible causes:")
    print("   - Gemini API not responding")
    print("   - API key invalid or rate limited")
    print("   - Network connectivity issues")
except Exception as e:
    print(f"❌ Code generation error: {e}")
    import traceback
    traceback.print_exc()

# Test 5: Full MAS with Enhancement
print("\n[5/5] Testing Full MAS with Enhancement...")
print("   Task: 'Implement binary search'")
print("   This will be SLOWER (~45-60 seconds) with 4 agents...")
print("   You can skip this by pressing Ctrl+C")

try:
    input("   Press Enter to continue or Ctrl+C to skip... ")
    
    start_time = time.time()
    r = requests.post(
        f"{BASE_URL}/api/run-mas",
        json={
            "task": "Implement binary search algorithm in Python",
            "language": "python",
            "use_full_mas": True
        },
        headers={"Authorization": f"Bearer {token}"},
        timeout=120  # 2 minute timeout
    )
    elapsed = time.time() - start_time
    
    if r.status_code == 200:
        result = r.json()
        print(f"✅ Full MAS completed in {elapsed:.1f}s")
        print(f"   Initial Score: {result.get('initial_score', 'N/A'):.3f}")
        print(f"   Final Score: {result.get('predicted_score', 'N/A'):.3f}")
        print(f"   Enhancement Loops: {result.get('enhancement_loops', 0)}")
        print(f"   Auto Enhanced: {result.get('auto_enhanced', False)}")
    else:
        print(f"❌ Full MAS failed: {r.status_code}")
        print(f"   Response: {r.text[:500]}")
        
except KeyboardInterrupt:
    print("\n⏭️  Skipped full MAS test")
except requests.Timeout:
    print(f"❌ Request timed out after 120 seconds")
except Exception as e:
    print(f"❌ Full MAS error: {e}")

print("\n" + "="*70)
print("TEST SUMMARY")
print("="*70)
print("\nIf tests 1-4 passed, your system is working correctly!")
print("If any test failed, check:")
print("  1. GEMINI_API_KEY is set correctly in backend/.env")
print("  2. GROQ_API_KEY is set correctly in backend/.env")
print("  3. MongoDB is running")
print("  4. No firewall blocking API calls")
print("="*70)
