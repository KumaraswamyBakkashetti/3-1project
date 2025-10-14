"""
Gemini API wrapper with automatic key rotation
Handles multiple API keys and switches when quota is exceeded
"""
import os
import google.generativeai as genai
from dotenv import load_dotenv
import time

# Load environment variables
load_dotenv()

class GeminiKeyManager:
    """Manages multiple Gemini API keys with automatic rotation"""
    
    def __init__(self):
        self.api_keys = self._load_api_keys()
        self.current_key_index = 0
        self.failed_keys = set()
        
        if not self.api_keys:
            raise ValueError("No Gemini API keys found in .env file")
        
        # Configure with first key
        self._configure_current_key()
    
    def _load_api_keys(self):
        """Load all GEMINI_API_KEY_* from environment"""
        keys = []
        i = 1
        while True:
            key = os.getenv(f'GEMINI_API_KEY_{i}')
            if key:
                keys.append(key)
                i += 1
            else:
                break
        return keys
    
    def _configure_current_key(self):
        """Configure genai with current API key"""
        if self.current_key_index < len(self.api_keys):
            current_key = self.api_keys[self.current_key_index]
            genai.configure(api_key=current_key)
            print(f"[INFO] Using Gemini API key #{self.current_key_index + 1}")
        else:
            raise Exception("All API keys exhausted")
    
    def rotate_key(self):
        """Switch to next available API key"""
        self.failed_keys.add(self.current_key_index)
        self.current_key_index += 1
        
        # Try to find next working key
        while self.current_key_index < len(self.api_keys):
            if self.current_key_index not in self.failed_keys:
                self._configure_current_key()
                return True
            self.current_key_index += 1
        
        # All keys exhausted
        return False
    
    def call_gemini(self, prompt, model_name="gemini-2.5-flash", timeout=20):
        """Call Gemini with timeout and speed optimization"""
        max_retries = min(3, len(self.api_keys))
        
        for attempt in range(max_retries):
            try:
                # Use faster model (gemini-1.5-flash is faster than 2.5-flash)
                if "gemini-2.5" in model_name:
                    model_name = "gemini-1.5-flash"  # Use faster version
                
                model = genai.GenerativeModel(model_name)
                
                # OPTIMIZED for speed: Lower tokens, higher temperature for faster generation
                generation_config = {
                    "max_output_tokens": 512,      # Reduced from 1024
                    "temperature": 0.3,            # Slightly higher for faster generation
                    "top_p": 0.8,                  # Reduce sampling space
                    "top_k": 20,                   # Limit token selection
                }
                
                response = model.generate_content(
                    prompt,
                    generation_config=generation_config
                )
                
                return response.text
                
            except Exception as e:
                error_msg = str(e).lower()
                
                # Quota error - rotate
                if "quota" in error_msg or "429" in error_msg or "rate limit" in error_msg:
                    if self.rotate_key():
                        time.sleep(0.5)
                        continue
                    else:
                        return "# Error: All API keys exhausted"
                else:
                    # Other error - return error message
                    return f"# Error: {error_msg[:100]}"
        
        return "# Error: Failed after retries"


# Global key manager instance
_key_manager = None

def get_key_manager():
    """Get or create the global key manager"""
    global _key_manager
    if _key_manager is None:
        _key_manager = GeminiKeyManager()
    return _key_manager


def gemini_call(prompt, model_name="gemini-2.5-flash"):
    """
    Simple function interface for calling Gemini with auto key rotation
    
    Args:
        prompt (str): The prompt to send to Gemini
        model_name (str): Model to use (default: gemini-2.5-flash)
                         - gemini-2.5-flash: Latest stable, FASTEST, best for code (RECOMMENDED)
                         - gemini-2.5-pro: Highest quality, use for complex reasoning
                         - gemini-flash-latest: Auto-updates to newest Flash
        
    Returns:
        str: The generated response
    """
    manager = get_key_manager()
    return manager.call_gemini(prompt, model_name)


# Backward compatibility aliases
call_gemini = gemini_call
llama_call = gemini_call  # For backward compatibility with code that used llama_call
