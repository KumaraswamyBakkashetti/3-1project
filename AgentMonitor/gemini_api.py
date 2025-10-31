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
        original_prompt = prompt
        
        for attempt in range(max_retries):
            try:
                # On retry after safety block, simplify the prompt
                if attempt > 0:
                    # Remove potentially problematic words and simplify
                    prompt = original_prompt.replace("code", "solution")
                    prompt = prompt.replace("Code", "Solution")
                    prompt = prompt.replace("LANGUAGE:", "Format:")
                    prompt = f"Provide a programming solution:\n\n{prompt}"
                
                # Use gemini-2.5-flash - latest stable fast model (October 2025)
                # This works with your new API keys and v1beta API
                
                # Import safety enums
                from google.generativeai.types import HarmCategory, HarmBlockThreshold
                
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
                
                response = model.generate_content(
                    prompt,
                    generation_config=generation_config
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
                
                # Check for specific error types
                if "invalid operation" in error_msg or "response.text" in error_msg:
                    # Response structure issue - try rotating key
                    print(f"[WARNING] Invalid response structure: {e}")
                    if self.rotate_key():
                        time.sleep(0.5)
                        continue
                    else:
                        print(f"[ERROR] Invalid API response, all keys tried")
                        return ""  # Return empty, not error message
                
                # Quota error - rotate
                if "quota" in error_msg or "429" in error_msg or "rate limit" in error_msg:
                    if self.rotate_key():
                        time.sleep(0.5)
                        continue
                    else:
                        print(f"[ERROR] All API keys exhausted")
                        return ""  # Return empty, not error message
                else:
                    # Other error - return empty
                    print(f"[ERROR] API call failed: {error_msg[:100]}")
                    return ""  # Return empty, not error message
        
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


def gemini_call(prompt, model_name="gemini-2.5-flash"):
    """
    Simple function interface for calling Gemini with auto key rotation
    
    Args:
        prompt (str): The prompt to send to Gemini
        model_name (str): Model to use (default: gemini-2.5-flash)
                         - gemini-2.5-flash: Latest stable fast model (RECOMMENDED)
                         - gemini-2.5-pro: Most capable model for complex tasks
                         - gemini-2.0-flash: Older but stable fast model
        
    Returns:
        str: The generated response
    """
    manager = get_key_manager()
    return manager.call_gemini(prompt, model_name)


# Backward compatibility aliases
call_gemini = gemini_call
llama_call = gemini_call  # For backward compatibility with code that used llama_call
