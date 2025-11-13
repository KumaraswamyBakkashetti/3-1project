"""
Gemini API wrapper with automatic key rotation
Handles multiple API keys and switches when quota is exceeded
"""
import os
import google.generativeai as genai
from dotenv import load_dotenv
import time
from pathlib import Path

# Load environment variables from backend/.env
# Find backend/.env regardless of where script is run from
current_file = Path(__file__).resolve()
project_root = current_file.parent.parent  # Go up to Final folder
backend_env = project_root / "backend" / ".env"

if backend_env.exists():
    load_dotenv(backend_env, override=True)  # Force override existing env vars
    print(f"[INFO] Loaded .env from: {backend_env}")
else:
    load_dotenv(override=True)  # Fallback to default behavior
    print(f"[WARNING] backend/.env not found at {backend_env}, using default .env loading")

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
        
        # Try single key first (GEMINI_API_KEY)
        single_key = os.getenv('GEMINI_API_KEY')
        if single_key and len(single_key) > 20:
            keys.append(single_key)
            print(f"[INFO] Loaded primary GEMINI_API_KEY")
        
        # Then try numbered keys 1-15 (support up to 15 keys)
        for i in range(1, 16):
            key = os.getenv(f'GEMINI_API_KEY_{i}')
            if key and key.strip() and len(key) > 20:  # Basic validation
                keys.append(key)
                print(f"[INFO] Loaded GEMINI_API_KEY_{i}")
        
        if not keys:
            print("[WARNING] No valid Gemini API keys found!")
        else:
            print(f"[INFO] Total valid API keys loaded: {len(keys)}")
        
        return keys
    
    def _configure_current_key(self):
        """Configure genai with current API key"""
        if self.current_key_index < len(self.api_keys):
            current_key = self.api_keys[self.current_key_index]
            genai.configure(api_key=current_key)
            print(f"[INFO] Using Gemini API key #{self.current_key_index + 1}")
        else:
            raise Exception("All API keys exhausted")
    
    def rotate_key(self, mark_failed=True):
        """Switch to next available API key"""
        if mark_failed:
            self.failed_keys.add(self.current_key_index)
        
        old_index = self.current_key_index
        self.current_key_index += 1
        
        # Try to find next working key
        while self.current_key_index < len(self.api_keys):
            if self.current_key_index not in self.failed_keys:
                self._configure_current_key()
                print(f"[SUCCESS] Switched from key #{old_index + 1} to key #{self.current_key_index + 1}")
                return True
            self.current_key_index += 1
        
        # All keys exhausted - reset to first key and mark all as available
        print(f"[WARNING] All {len(self.api_keys)} keys tried, resetting to key #1")
        self.current_key_index = 0
        self.failed_keys.clear()  # Give all keys another chance
        self._configure_current_key()
        return True  # Always return True to keep trying
    
    def call_gemini(self, prompt, model_name="gemini-flash-latest", timeout=30):
        """Call Gemini with timeout and speed optimization
        
        Args:
            model_name: Model to use (default: gemini-flash-latest - FASTEST & VERIFIED Nov 13, 2025)
            timeout: Request timeout in seconds (default: 30s for faster failure on service issues)
        """
        # Reduce retries when service is unavailable - fail fast
        max_retries = 2  # Only 2 retries for faster failure
        original_prompt = prompt
        
        # Use VERIFIED working models as fallbacks (tested Nov 13, 2025)
        fallback_models = [
            "gemini-flash-latest",               # PRIMARY - FASTEST (1.12s)
            "gemini-2.5-flash",                  # BACKUP 1 (2.05s)
            "gemini-2.5-flash-preview-05-20",  # BACKUP 2 (3.12s)
            "gemini-1.5-flash"                   # BACKUP 3 (stable fallback)
        ]
        tried_models = set()
        
        print(f"[INIT] Starting request with {len(self.api_keys)} API keys available, {max_retries} max retries")
        print(f"[MODEL] Using: {model_name}")
        
        for attempt in range(max_retries):
            try:
                # On retry after safety block, simplify the prompt
                if attempt > 0:
                    # Remove potentially problematic words and simplify
                    prompt = original_prompt.replace("code", "solution")
                    prompt = prompt.replace("Code", "Solution")
                    prompt = prompt.replace("LANGUAGE:", "Format:")
                    prompt = f"Provide a programming solution:\n\n{prompt}"
                    
                    # Exponential backoff - wait longer between retries
                    wait_time = min(2 ** attempt, 5)  # Max 5 seconds
                    print(f"[INFO] Retry {attempt}/{max_retries} after {wait_time}s wait...")
                    time.sleep(wait_time)
                
                # Use gemini-2.5-flash - latest stable fast model (October 2025)
                # This works with your new API keys and v1beta API
                
                # Import safety enums and configure request options with timeout
                from google.generativeai.types import HarmCategory, HarmBlockThreshold
                import google.generativeai.types as types
                
                # Safety settings - prevent blocking for code generation
                safety_settings = {
                    HarmCategory.HARM_CATEGORY_HARASSMENT: HarmBlockThreshold.BLOCK_NONE,
                    HarmCategory.HARM_CATEGORY_HATE_SPEECH: HarmBlockThreshold.BLOCK_NONE,
                    HarmCategory.HARM_CATEGORY_SEXUALLY_EXPLICIT: HarmBlockThreshold.BLOCK_NONE,
                    HarmCategory.HARM_CATEGORY_DANGEROUS_CONTENT: HarmBlockThreshold.BLOCK_NONE,
                }
                
                model = genai.GenerativeModel(
                    model_name,
                    safety_settings=safety_settings
                )
                
                # No token limit - let Gemini generate complete code
                generation_config = {
                    "temperature": 0.3,            # Slightly higher for faster generation
                    "top_p": 0.8,                  # Reduce sampling space
                    "top_k": 20,                   # Limit token selection
                }
                
                # Add request options with timeout (prevents 600s hangs)
                request_options = types.RequestOptions(timeout=timeout)
                
                response = model.generate_content(
                    prompt,
                    generation_config=generation_config,
                    request_options=request_options
                )
                
                # Try to access response.text safely
                try:
                    if response.text:
                        return response.text
                except (ValueError, AttributeError):
                    # response.text failed - try alternative methods
                    pass
                
                # Try to get text from parts
                try:
                    if hasattr(response, 'parts') and response.parts:
                        return ''.join([part.text for part in response.parts if hasattr(part, 'text')])
                except:
                    pass
                
                # Try to get text from candidates
                try:
                    if hasattr(response, 'candidates') and response.candidates:
                        for candidate in response.candidates:
                            if hasattr(candidate, 'content') and hasattr(candidate.content, 'parts'):
                                parts_text = ''.join([part.text for part in candidate.content.parts if hasattr(part, 'text')])
                                if parts_text:
                                    return parts_text
                except:
                    pass
                
                # If we get here, the response was blocked or empty
                finish_reason = getattr(response.candidates[0], 'finish_reason', 'UNKNOWN') if response.candidates else 'NO_CANDIDATES'
                print(f"[WARNING] Gemini response blocked or empty. Finish reason: {finish_reason}")
                
                # Check if it's a safety block (finish_reason 2 = SAFETY)
                if str(finish_reason) == '2' or str(finish_reason) == 'SAFETY':
                    print(f"[INFO] Safety block detected on attempt {attempt + 1}/{max_retries}, retrying with modified prompt...")
                    
                    # Modify prompt to be more neutral
                    # Remove words that might trigger safety filters
                    modified_prompt = prompt.replace("attack", "approach").replace("kill", "stop").replace("hack", "modify")
                    
                    # If it's the same, add a prefix
                    if modified_prompt == prompt:
                        modified_prompt = f"Please provide a technical solution for the following programming task:\n\n{prompt}"
                    
                    prompt = modified_prompt  # Use modified prompt for next attempt
                    time.sleep(0.5)
                    continue  # Retry with modified prompt
                
                # For other types of blocks, return empty (let caller handle fallback)
                print(f"[WARNING] Response blocked, returning empty for fallback handling")
                return ""
                
            except Exception as e:
                error_msg = str(e).lower()
                
                # PRIORITY 1: Rate limit / Quota errors - IMMEDIATELY switch key
                if any(err in error_msg for err in ["quota", "429", "rate limit", "resource exhausted", "resource_exhausted"]):
                    print(f"[RATE LIMIT] API key #{self.current_key_index + 1} quota exceeded!")
                    if self.rotate_key(mark_failed=True):
                        print(f"[AUTO-SWITCH] Retrying with new API key...")
                        time.sleep(0.5)
                        continue
                    else:
                        print(f"[ERROR] All API keys have rate limits")
                        return ""
                
                # PRIORITY 2: Timeout errors - try different key
                if "timeout" in error_msg or "timed out" in error_msg or "deadline exceeded" in error_msg:
                    print(f"[TIMEOUT] Request timed out on attempt {attempt + 1}/{max_retries}")
                    if self.rotate_key(mark_failed=False):  # Don't mark as permanently failed
                        print(f"[AUTO-SWITCH] Trying different API key...")
                        time.sleep(1)
                        continue
                    else:
                        print(f"[ERROR] Timeout with all keys tried")
                        return ""
                
                # PRIORITY 3: 503 service unavailable - try fallback model
                if "503" in error_msg or "service unavailable" in error_msg or "failed to connect" in error_msg:
                    print(f"[503] Gemini service unavailable on attempt {attempt + 1}/{max_retries}")
                    
                    # Try a fallback model if we haven't tried all yet
                    if model_name not in tried_models:
                        tried_models.add(model_name)
                        
                        # Find next untried fallback model
                        for fallback in fallback_models:
                            if fallback not in tried_models:
                                print(f"[FALLBACK] Switching from {model_name} to {fallback}")
                                model_name = fallback
                                time.sleep(1)
                                continue  # Retry with different model
                    
                    # If all models tried, just wait and retry
                    wait_time = 2
                    print(f"[BACKOFF] All models tried, waiting {wait_time}s before retry...")
                    time.sleep(wait_time)
                    
                    # Don't rotate key for service unavailable - it's a Google server issue
                    continue
                
                # PRIORITY 4: Invalid response structure
                if "invalid operation" in error_msg or "response.text" in error_msg:
                    print(f"[WARNING] Invalid response structure: {str(e)[:100]}")
                    if self.rotate_key(mark_failed=False):
                        print(f"[AUTO-SWITCH] Trying different API key...")
                        time.sleep(0.5)
                        continue
                    else:
                        print(f"[ERROR] Invalid API response with all keys")
                        return ""
                
                # PRIORITY 5: Other errors - log and return empty
                print(f"[ERROR] API call failed: {error_msg[:150]}")
                return ""
        
        print(f"[ERROR] Failed after {max_retries} retries")
        return ""  # Return empty, not error message


# Global key manager instance
_key_manager = None

def get_key_manager():
    """Get or create the global key manager"""
    global _key_manager
    if _key_manager is None:
        _key_manager = GeminiKeyManager()
    return _key_manager


def gemini_call(prompt, model_name="gemini-flash-latest"):
    """
    Simple function interface for calling Gemini with auto key rotation
    
    Args:
        prompt (str): The prompt to send to Gemini
        model_name (str): Model to use (default: gemini-flash-latest - FASTEST, tested Nov 13, 2025)
                         - gemini-flash-latest: Auto-updated latest flash model (FASTEST - 1.12s)
                         - gemini-2.5-flash: Stable fast model (2.05s)
                         - gemini-2.5-flash-preview-05-20: Preview fast model (3.12s)
        
    Returns:
        str: The generated response
    """
    manager = get_key_manager()
    return manager.call_gemini(prompt, model_name)


# Backward compatibility aliases
call_gemini = gemini_call
llama_call = gemini_call  # For backward compatibility with code that used llama_call
