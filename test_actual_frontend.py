"""
Test the actual MAS execution with timing
"""
import requests
import time
import json

# API endpoint
API_URL = "http://localhost:8080/api"

# Test credentials (default admin account)
USERNAME = "admin"
PASSWORD = "admin123"

def test_mas_execution():
    print("=" * 60)
    print("🧪 TESTING MAS EXECUTION FROM FRONTEND")
    print("=" * 60)
    
    # Step 1: Login
    print("\n1️⃣ Logging in...")
    login_data = {
        "username": USERNAME,
        "password": PASSWORD
    }
    
    try:
        response = requests.post(f"{API_URL}/login", json=login_data)
        response.raise_for_status()
        token = response.json()["token"]
        print(f"   ✅ Login successful! Token: {token[:20]}...")
    except Exception as e:
        print(f"   ❌ Login failed: {e}")
        return
    
    # Step 2: Submit code generation task
    print("\n2️⃣ Submitting task...")
    task = "Write a function to add two numbers"
    print(f"   Task: '{task}'")
    
    task_data = {
        "task": task,
        "code": ""
    }
    
    headers = {
        "Authorization": f"Bearer {token}"
    }
    
    print("\n⏱️  Starting timer...")
    start_time = time.time()
    
    try:
        response = requests.post(
            f"{API_URL}/run_mas",
            json=task_data,
            headers=headers,
            timeout=120  # 2 minute timeout
        )
        
        elapsed_time = time.time() - start_time
        
        response.raise_for_status()
        result = response.json()
        
        print("\n" + "=" * 60)
        print(f"⏱️  EXECUTION TIME: {elapsed_time:.2f} seconds")
        print("=" * 60)
        
        # Print output
        print("\n📤 OUTPUT RECEIVED:")
        print("-" * 60)
        output = result.get("output", "")
        print(output)
        print("-" * 60)
        
        # Analyze output
        print("\n📊 OUTPUT ANALYSIS:")
        print(f"   • Length: {len(output)} characters")
        print(f"   • Lines: {output.count(chr(10)) + 1}")
        print(f"   • Has markdown (```): {'✅ YES' if '```' in output else '❌ NO'}")
        print(f"   • Has 'def': {'✅ YES' if 'def ' in output else '❌ NO'}")
        print(f"   • Has explanations: {'⚠️ YES' if any(word in output.lower() for word in ['this function', 'here', 'example', 'usage']) else '✅ NO'}")
        
        # Print other response data
        print("\n📈 RESPONSE DATA:")
        print(f"   • Predicted Score: {result.get('predicted_score', 'N/A')}")
        print(f"   • Run ID: {result.get('run_id', 'N/A')}")
        
        # Check if it's clean code
        print("\n🎯 CODE QUALITY CHECK:")
        if '```' in output:
            print("   ⚠️ WARNING: Output contains markdown blocks")
        if 'this function' in output.lower() or 'here' in output.lower():
            print("   ⚠️ WARNING: Output contains explanations")
        if len(output) > 500:
            print(f"   ⚠️ WARNING: Output is verbose ({len(output)} chars)")
        
        if '```' not in output and len(output) < 300 and 'def ' in output:
            print("   ✅ OUTPUT LOOKS CLEAN!")
        else:
            print("   ❌ OUTPUT NEEDS CLEANUP")
        
    except requests.exceptions.Timeout:
        elapsed_time = time.time() - start_time
        print(f"\n❌ REQUEST TIMED OUT after {elapsed_time:.2f} seconds")
    except Exception as e:
        elapsed_time = time.time() - start_time
        print(f"\n❌ ERROR after {elapsed_time:.2f} seconds: {e}")
        if hasattr(e, 'response') and e.response is not None:
            print(f"   Response: {e.response.text[:500]}")

if __name__ == "__main__":
    print("\n🚀 Testing MAS Code Generation")
    print("   This simulates a real frontend request\n")
    test_mas_execution()
    print("\n✅ Test complete!\n")
