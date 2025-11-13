"""
Quick check: Is the backend using the NEW model?
Reads the currently running backend process output or checks the code
"""
import sys
from pathlib import Path

# Read gemini_api.py to verify the model
gemini_file = Path(__file__).parent / "AgentMonitor" / "gemini_api.py"

if gemini_file.exists():
    content = gemini_file.read_text()
    
    # Check for the model being used
    lines = content.split('\n')
    
    print("=" * 80)
    print("🔍 CHECKING CURRENT MODEL CONFIGURATION")
    print("=" * 80)
    
    for i, line in enumerate(lines, 1):
        if 'def call_gemini' in line and 'model_name=' in line:
            # Found the function definition with default model
            print(f"\nLine {i}: {line.strip()}")
            
            if 'gemini-flash-latest' in line:
                print("✅ CORRECT: Using gemini-flash-latest (FASTEST)")
            elif 'gemini-2.5-flash' in line:
                print("❌ OLD MODEL: Still using gemini-2.5-flash (SLOW, TIMES OUT)")
                print("\n🔧 FIX NEEDED:")
                print("   1. The code was updated but backend didn't restart")
                print("   2. Press Ctrl+C in the backend terminal")
                print("   3. Run: python app.py")
            else:
                print(f"⚠️ UNKNOWN MODEL in line")
        
        elif 'def gemini_call' in line and 'model_name=' in line:
            # Found the standalone function with default model
            print(f"\nLine {i}: {line.strip()}")
            
            if 'gemini-flash-latest' in line:
                print("✅ CORRECT: Using gemini-flash-latest (FASTEST)")
            elif 'gemini-2.5-flash' in line:
                print("❌ OLD MODEL: Still using gemini-2.5-flash")
    
    print("\n" + "=" * 80)
    print("💡 EXPECTED STARTUP LOG from backend:")
    print("=" * 80)
    print("[MODEL] Using: gemini-flash-latest  ✅")
    print("\nIf you see '[MODEL] Using: gemini-2.5-flash', the backend needs restart!")
    print("=" * 80)
    
else:
    print(f"❌ gemini_api.py not found at {gemini_file}")
