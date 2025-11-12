"""
Direct test of Gemini API to check if service is available
"""
import os
from dotenv import load_dotenv
import google.generativeai as genai

load_dotenv('backend/.env')

api_key = os.getenv('GEMINI_API_KEY')
print(f"Testing with API key: {api_key[:20]}...{api_key[-10:]}")

try:
    genai.configure(api_key=api_key)
    
    # Try multiple models
    models_to_test = [
        "gemini-1.5-flash",
        "gemini-2.0-flash-exp", 
        "gemini-pro"
    ]
    
    for model_name in models_to_test:
        print(f"\n{'='*60}")
        print(f"Testing: {model_name}")
        print('='*60)
        
        try:
            model = genai.GenerativeModel(model_name)
            response = model.generate_content("Write a simple hello world in Python")
            
            if response.text:
                print(f"✅ SUCCESS! Model {model_name} is working!")
                print(f"Response length: {len(response.text)} chars")
                print(f"Response preview: {response.text[:150]}...")
                break
            else:
                print(f"⚠️  Model {model_name} returned empty response")
                
        except Exception as e:
            error_msg = str(e)
            if "503" in error_msg or "Service Unavailable" in error_msg:
                print(f"❌ Model {model_name} - Service Unavailable (503)")
            elif "404" in error_msg or "not found" in error_msg:
                print(f"❌ Model {model_name} - Not Found (404)")
            elif "429" in error_msg or "quota" in error_msg.lower():
                print(f"❌ Model {model_name} - Quota Exceeded (429)")
            else:
                print(f"❌ Model {model_name} - Error: {error_msg[:100]}")
    
    print(f"\n{'='*60}")
    print("CONCLUSION:")
    print('='*60)
    print("If ALL models failed with 503, Google's Gemini API service is down.")
    print("If some work, try using the working model in your code.")
    print("If you get 404 errors, the model name might be incorrect for your API version.")
    
except Exception as e:
    print(f"❌ FATAL ERROR: {e}")
    print("\nPossible causes:")
    print("1. Invalid API key")
    print("2. Network connectivity issues")
    print("3. Google API service is completely down")
