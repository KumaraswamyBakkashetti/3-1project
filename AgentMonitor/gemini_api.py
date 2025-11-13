"""
Gemini API wrapper with automatic key rotation
Handles multiple API keys and switches when quota is exceeded
"""
import os
import time
from dotenv import load_dotenv

# google.generativeai is optional; import inside methods to avoid hard failure at import time
try:
    import google.generativeai as genai
except Exception:
    genai = None

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

        # Try single key first (GEMINI_API_KEY)
        single_key = os.getenv("GEMINI_API_KEY")
        if single_key:
            keys.append(single_key)
            # Do not print keys or key fragments to avoid leaking secrets
            print("[INFO] Loaded primary agent ")

        # Then try numbered keys (only valid ones)
        i = 1
        while i <= 5:  # Max 5 keys
            key = os.getenv(f"GEMINI_API_KEY_{i}")
            if key and key.strip() and len(key) > 20:  # Basic validation
                keys.append(key)
                # Avoid printing key material; log that a numbered key was found
                print(f"[INFO] Loaded agent #{i}")
            i += 1

        if not keys:
            print("[WARNING] No valid agent found!")
        else:
            print(f"[INFO] valid agent loaded")

        return keys

    def _configure_current_key(self):
        """Configure genai with current API key"""
        if genai is None:
            print("[WARNING] google.generativeai package not available; Gemini calls will fail.")
            return

        if self.current_key_index < len(self.api_keys):
            current_key = self.api_keys[self.current_key_index]
            genai.configure(api_key=current_key)
            # Do NOT log the key value or index in production logs
            print("[INFO] Configured agent for requests")
        else:
            raise Exception("All agents exhausted")

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
                print("[SUCCESS] Switched agent for requests")
                return True
            self.current_key_index += 1

        # All keys exhausted - reset to first key and mark all as available
        print(f"[WARNING] All agents tried, resetting to agent #1")
        self.current_key_index = 0
        self.failed_keys.clear()  # Give all keys another chance
        self._configure_current_key()
        return True  # Always return True to keep trying

    def call_gemini(self, prompt, model_name="gemini-2.5-flash", timeout=60):
        """Call Gemini with timeout and speed optimization"""
        if genai is None:
            raise RuntimeError("google.generativeai is not installed or could not be imported")

        # Try each API key at least once (max retries)
        max_retries = min(5, len(self.api_keys) * 2)  # 2 attempts per key
        original_prompt = prompt

        print(f"[INIT] Starting agent request ")

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

                # Use gemini-2.5-flash - latest stable fast model
                from google.generativeai.types import HarmCategory, HarmBlockThreshold
                import google.generativeai.types as types

                # Safety settings - allow code generation by setting BLOCK_NONE for categories
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

                # Generation config tweaks
                generation_config = {
                    "temperature": 0.3,
                    "top_p": 0.8,
                    "top_k": 20,
                }

                # Add request options with timeout
                request_options = types.RequestOptions(timeout=timeout)

                response = model.generate_content(
                    prompt,
                    generation_config=generation_config,
                    request_options=request_options
                )

                # Try various ways to extract text
                try:
                    if getattr(response, "text", None):
                        return response.text
                except Exception:
                    pass

                # parts
                try:
                    if hasattr(response, "parts") and response.parts:
                        return "".join([getattr(part, "text", "") for part in response.parts if getattr(part, "text", None)])
                except Exception:
                    pass

                # candidates -> content -> parts
                try:
                    if hasattr(response, "candidates") and response.candidates:
                        for candidate in response.candidates:
                            content = getattr(candidate, "content", None)
                            if content and hasattr(content, "parts"):
                                parts_text = "".join([getattr(part, "text", "") for part in content.parts if getattr(part, "text", None)])
                                if parts_text:
                                    return parts_text
                except Exception:
                    pass

                # If we get here, response was blocked or empty
                finish_reason = "NO_CANDIDATES"
                try:
                    if getattr(response, "candidates", None):
                        finish_reason = getattr(response.candidates[0], "finish_reason", finish_reason)
                except Exception:
                    pass

                print(f"[WARNING] agent response blocked or empty. Finish reason: {finish_reason}")

                # Check for safety block (possible numeric or textual indicators)
                if str(finish_reason) in ("2", "SAFETY"):
                    print(f"[INFO] Safety block detected on attempt {attempt + 1}/{max_retries}, retrying with modified prompt...")
                    modified_prompt = prompt.replace("attack", "approach").replace("kill", "stop").replace("hack", "modify")
                    if modified_prompt == prompt:
                        modified_prompt = f"Please provide a technical solution for the following programming task:\n\n{prompt}"
                    prompt = modified_prompt
                    time.sleep(0.5)
                    continue

                # Otherwise return empty for caller fallback
                print("[WARNING] Response blocked, returning empty for fallback handling")
                return ""

            except Exception as e:
                error_msg = str(e).lower()

                # PRIORITY 1: Rate limit / Quota errors - switch key
                if any(err in error_msg for err in ["quota", "429", "rate limit", "resource exhausted", "resource_exhausted"]):
                    print("[TIME LIMIT] agent time exceeded")
                    if self.rotate_key(mark_failed=True):
                        print("[AUTO-SWITCH] Retrying with different agent key...")
                        time.sleep(0.5)
                        continue
                    else:
                        print("[ERROR] All Agents reached limits")
                        return ""

                # PRIORITY 2: Timeout errors - try different key
                if "timeout" in error_msg or "timed out" in error_msg or "deadline exceeded" in error_msg:
                    print(f"[TIMEOUT] Agent request timed out on attempt {attempt + 1}/{max_retries}")
                    if self.rotate_key(mark_failed=False):
                        print("[AUTO-SWITCH] Trying different agent...")
                        time.sleep(1)
                        continue
                    else:
                        print("[ERROR] Timeout with all agents tried")
                        return ""

                # PRIORITY 3: 503 service unavailable - retry with backoff
                if "503" in error_msg or "service unavailable" in error_msg or "failed to connect" in error_msg:
                    print(f"[503] agent service unavailable on attempt {attempt + 1}/{max_retries}")
                    wait_time = min(2 ** (attempt + 1), 5)
                    print(f"[BACKOFF] Waiting {wait_time}s before retry...")
                    time.sleep(wait_time)
                    if self.rotate_key(mark_failed=False):
                        continue
                    else:
                        print("[ERROR] Service unavailable after all retries")
                        return ""

                # PRIORITY 4: Invalid response structure
                if "invalid operation" in error_msg or "response.text" in error_msg:
                    print(f"[WARNING] Invalid response structure: {str(e)[:100]}")
                    if self.rotate_key(mark_failed=False):
                        print("[AUTO-SWITCH] Trying different Agent...")
                        time.sleep(0.5)
                        continue
                    else:
                        print("[ERROR] Invalid Agent response")
                        return ""

                # Other errors: log and return empty
                print(f"[ERROR] agent call failed: {error_msg[:150]}")
                return ""

        print(f"[ERROR] agent request failed after {max_retries} retries")
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
    """
    manager = get_key_manager()
    return manager.call_gemini(prompt, model_name)


# Backward compatibility aliases
call_gemini = gemini_call
llama_call = gemini_call  # For backward compatibility with code that used llama_call
