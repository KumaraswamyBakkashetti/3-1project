"""
List actual available model names
"""
import google.generativeai as genai

# Use the active key
api_key = "AIzaSyAiHwhNZcjHtkFuDwmo57Bwnecfxnd5ltU"
genai.configure(api_key=api_key)

print("AVAILABLE GEMINI MODELS FOR CODE GENERATION:")
print("="*70)

for model in genai.list_models():
    if 'generateContent' in model.supported_generation_methods:
        # Extract just the model name (remove 'models/' prefix)
        model_name = model.name.replace('models/', '')
        print(f"✅ {model_name}")
        
print("\n" + "="*70)
print("TESTING THE BEST MODELS:")
print("="*70)

# Test a few promising models
test_models = []
for model in genai.list_models():
    if 'generateContent' in model.supported_generation_methods:
        name = model.name.replace('models/', '')
        if 'flash' in name.lower() or 'pro' in name.lower():
            test_models.append(name)

for model_name in test_models[:5]:  # Test first 5
    print(f"\nTesting: {model_name}")
    try:
        model = genai.GenerativeModel(model_name)
        response = model.generate_content("Write hello world in Python", request_options={'timeout': 10})
        if response.text:
            print(f"  ✅ WORKS! Response: {len(response.text)} chars")
            print(f"  Preview: {response.text[:80]}...")
            print(f"  👉 RECOMMENDED MODEL: {model_name}")
            break
    except Exception as e:
        print(f"  ❌ Failed: {str(e)[:60]}")
