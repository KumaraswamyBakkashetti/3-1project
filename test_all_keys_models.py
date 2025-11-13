"""
Comprehensive API Key & Model Testing
Tests all 3 keys with multiple Gemini models to find working combinations
"""
import os
from pathlib import Path
from dotenv import load_dotenv
import google.generativeai as genai
import time

# Load backend/.env
backend_env = Path(__file__).parent / "backend" / ".env"
load_dotenv(backend_env, override=True)
print(f"✓ Loaded .env from: {backend_env}\n")

# Simple test prompt
TEST_PROMPT = "Write a simple Java function to reverse a string. Just the function, no explanation."

# Models to test (prioritized list)
MODELS_TO_TEST = [
    "gemini-2.5-flash-preview-05-20",  # Previously working model
    "gemini-2.5-flash",                 # Current default in code
    "gemini-2.0-flash-exp",             # Fast experimental
    "gemini-flash-latest",              # Auto-updated latest
    "gemini-1.5-flash",                 # Stable fallback
    "gemini-1.5-pro",                   # Pro fallback
]

def test_key_with_model(key_name, api_key, model_name):
    """Test a single key+model combination"""
    
    if not api_key or len(api_key) < 30:
        return {"status": "INVALID_KEY", "error": "Key too short or missing"}
    
    try:
        # Configure with this key
        genai.configure(api_key=api_key)
        
        # Import safety settings
        from google.generativeai.types import HarmCategory, HarmBlockThreshold
        import google.generativeai.types as types
        
        safety_settings = {
            HarmCategory.HARM_CATEGORY_HARASSMENT: HarmBlockThreshold.BLOCK_NONE,
            HarmCategory.HARM_CATEGORY_HATE_SPEECH: HarmBlockThreshold.BLOCK_NONE,
            HarmCategory.HARM_CATEGORY_SEXUALLY_EXPLICIT: HarmBlockThreshold.BLOCK_NONE,
            HarmCategory.HARM_CATEGORY_DANGEROUS_CONTENT: HarmBlockThreshold.BLOCK_NONE,
        }
        
        model = genai.GenerativeModel(model_name, safety_settings=safety_settings)
        request_options = types.RequestOptions(timeout=15)  # Short timeout for testing
        
        start = time.time()
        response = model.generate_content(
            TEST_PROMPT,
            generation_config={"temperature": 0.3},
            request_options=request_options
        )
        elapsed = time.time() - start
        
        # Extract text
        result_text = None
        try:
            result_text = response.text
        except:
            if hasattr(response, 'candidates') and response.candidates:
                try:
                    result_text = ''.join([part.text for part in response.candidates[0].content.parts])
                except:
                    pass
        
        if result_text and len(result_text) > 20:
            return {
                "status": "SUCCESS",
                "chars": len(result_text),
                "time": round(elapsed, 2),
                "preview": result_text[:100]
            }
        else:
            finish_reason = getattr(response.candidates[0], 'finish_reason', 'UNKNOWN') if response.candidates else 'NO_RESPONSE'
            return {"status": "BLOCKED", "error": f"Finish reason: {finish_reason}"}
            
    except Exception as e:
        error_str = str(e)
        
        # Categorize error
        if '503' in error_str or 'Service Unavailable' in error_str:
            return {"status": "503_SERVICE_DOWN", "error": "Gemini servers unavailable"}
        elif '429' in error_str or 'quota' in error_str.lower() or 'rate' in error_str.lower():
            return {"status": "429_QUOTA", "error": "Quota/rate limit exceeded"}
        elif '403' in error_str or 'API_KEY_INVALID' in error_str or 'api key not valid' in error_str:
            return {"status": "403_INVALID_KEY", "error": "Invalid or leaked API key"}
        elif '400' in error_str or 'api key not found' in error_str.lower():
            return {"status": "400_BAD_REQUEST", "error": "Bad request or expired key"}
        elif 'timeout' in error_str.lower():
            return {"status": "TIMEOUT", "error": "Request timed out"}
        elif 'not found' in error_str.lower() or 'does not exist' in error_str.lower():
            return {"status": "MODEL_NOT_FOUND", "error": "Model doesn't exist"}
        else:
            return {"status": "ERROR", "error": error_str[:100]}

def print_result(key_name, model_name, result):
    """Pretty print test result"""
    status = result["status"]
    
    # Color coding
    if status == "SUCCESS":
        icon = "✅"
        color = ""
    elif status in ["403_INVALID_KEY", "400_BAD_REQUEST"]:
        icon = "🔴"
        color = ""
    elif status in ["503_SERVICE_DOWN", "429_QUOTA"]:
        icon = "🟡"
        color = ""
    elif status == "TIMEOUT":
        icon = "⏱️"
        color = ""
    elif status == "MODEL_NOT_FOUND":
        icon = "❓"
        color = ""
    else:
        icon = "⚠️"
        color = ""
    
    # Build output
    key_short = key_name.replace("GEMINI_API_KEY", "KEY")
    model_short = model_name.replace("gemini-", "")
    
    if status == "SUCCESS":
        print(f"  {icon} {key_short:10s} + {model_short:25s} → {result['chars']}ch in {result['time']}s")
    else:
        print(f"  {icon} {key_short:10s} + {model_short:25s} → {status}")

def main():
    print("=" * 80)
    print("🔑 TESTING ALL API KEYS WITH MULTIPLE GEMINI MODELS")
    print("=" * 80)
    
    # Get keys
    keys = [
        ("GEMINI_API_KEY", os.getenv('GEMINI_API_KEY')),
        ("GEMINI_API_KEY_1", os.getenv('GEMINI_API_KEY_1')),
        ("GEMINI_API_KEY_2", os.getenv('GEMINI_API_KEY_2')),
    ]
    
    print(f"\n📋 Testing {len(keys)} keys × {len(MODELS_TO_TEST)} models = {len(keys) * len(MODELS_TO_TEST)} combinations\n")
    
    # Store all results
    all_results = {}
    working_combos = []
    
    # Test each key with each model
    for key_name, api_key in keys:
        if not api_key:
            print(f"⚠️  {key_name}: NOT SET\n")
            continue
        
        print(f"\n{'─' * 80}")
        print(f"Testing: {key_name} (ends with ...{api_key[-8:]})")
        print(f"{'─' * 80}")
        
        for model_name in MODELS_TO_TEST:
            result = test_key_with_model(key_name, api_key, model_name)
            combo_key = f"{key_name}_{model_name}"
            all_results[combo_key] = result
            
            print_result(key_name, model_name, result)
            
            # Track working combinations
            if result["status"] == "SUCCESS":
                working_combos.append({
                    "key": key_name,
                    "model": model_name,
                    "time": result["time"],
                    "chars": result["chars"]
                })
            
            # Small delay between tests
            time.sleep(0.5)
    
    # Summary
    print("\n" + "=" * 80)
    print("📊 SUMMARY & RECOMMENDATIONS")
    print("=" * 80)
    
    if working_combos:
        print(f"\n✅ Found {len(working_combos)} working combination(s):\n")
        
        # Sort by speed (fastest first)
        working_combos.sort(key=lambda x: x["time"])
        
        for i, combo in enumerate(working_combos, 1):
            print(f"  {i}. {combo['key']:18s} + {combo['model']:30s}")
            print(f"     ⚡ {combo['time']}s | {combo['chars']} chars")
            if i == 1:
                print(f"     👈 RECOMMENDED (fastest)")
        
        # Print code update recommendation
        best = working_combos[0]
        print(f"\n💡 UPDATE YOUR CODE:")
        print(f"   File: AgentMonitor/gemini_api.py")
        print(f"   Line 299: Change default model to: \"{best['model']}\"")
        print(f"\n   Then restart backend:")
        print(f"   cd backend")
        print(f"   python app.py")
        
    else:
        print("\n❌ NO WORKING COMBINATIONS FOUND\n")
        
        # Analyze failures
        status_counts = {}
        for result in all_results.values():
            status = result["status"]
            status_counts[status] = status_counts.get(status, 0) + 1
        
        print("Failure breakdown:")
        for status, count in sorted(status_counts.items(), key=lambda x: -x[1]):
            print(f"  • {status}: {count} times")
        
        print("\n🔧 TROUBLESHOOTING:")
        
        if any("503" in r["status"] for r in all_results.values()):
            print("  1. ⏰ Gemini service is down - wait 10-30 min and retry")
            print("     Check: https://status.cloud.google.com")
        
        if any("403" in r["status"] or "400" in r["status"] for r in all_results.values()):
            print("  2. 🔑 API keys are invalid/expired/leaked")
            print("     → Go to https://aistudio.google.com/apikey")
            print("     → Delete old keys and create 3 NEW keys")
            print("     → Update backend/.env with new keys")
        
        if any("429" in r["status"] for r in all_results.values()):
            print("  3. 📊 Quota exceeded - wait for daily reset or upgrade plan")
        
        if any("MODEL_NOT_FOUND" in r["status"] for r in all_results.values()):
            print("  4. 🤖 Some models don't exist - stick to working models")
    
    print("\n" + "=" * 80)

if __name__ == "__main__":
    main()
