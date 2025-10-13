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
    
    def call_gemini(self, prompt, model_name="gemini-2.5-flash"):
        """
        Call Gemini with automatic key rotation on quota errors
        
        Args:
            prompt (str): The prompt to send
            model_name (str): Gemini model to use
                             - gemini-2.5-flash: Latest stable, FASTEST (RECOMMENDED)
                             - gemini-2.5-pro: Highest quality, slower
                             - gemini-flash-latest: Auto-updates to newest
            
        Returns:
            str: Generated response
        """
        max_retries = len(self.api_keys)
        
        for attempt in range(max_retries):
            try:
                model = genai.GenerativeModel(model_name)
                response = model.generate_content(prompt)
                return response.text
                
            except Exception as e:
                error_msg = str(e).lower()
                
                # Check if it's a quota/rate limit error
                if "quota" in error_msg or "429" in error_msg or "rate limit" in error_msg:
                    print(f"[WARNING] API key #{self.current_key_index + 1} quota exceeded")
                    
                    if self.rotate_key():
                        print(f"[INFO] Switched to API key #{self.current_key_index + 1}")
                        time.sleep(1)  # Brief delay before retry
                        continue
                    else:
                        raise Exception("All Gemini API keys exhausted. Please wait or add more keys.")
                else:
                    # Other error, don't rotate
                    raise e
        
        raise Exception("Failed to get response after trying all API keys")


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
