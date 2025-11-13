"""
Groq API Wrapper - 100% FREE API for LLM judging/scoring

Groq provides FREE ultra-fast inference with generous limits:
- 30 requests per minute
- No credit card required
- Models: Llama 3.1, Mixtral, Gemma

Perfect for code scoring and enhancement feedback!
"""
import os
import time
import requests
from typing import Optional
from pathlib import Path
from dotenv import load_dotenv

# Load .env file from this directory or parent if present
env_path = Path(__file__).parent / ".env"
if env_path.exists():
    load_dotenv(env_path)
else:
    env_path = Path(__file__).parent.parent / ".env"
    if env_path.exists():
        load_dotenv(env_path)


class GroqAPI:
    """
    Groq API wrapper for FREE LLM inference

    Usage:
        groq = GroqAPI()
        response = groq._call("Rate this code...")
    """

    def __init__(self, api_key: Optional[str] = None):
        """
        Args:
            api_key: Groq API key (or set GROQ_API_KEY env var)
        """
        self.api_key = api_key or os.getenv("GROQ_API_KEY")

        if not self.api_key:
            raise ValueError(
                "Groq API key required!\n"
                "1. Sign up: https://console.groq.com\n"
                "2. Get key: https://console.groq.com/keys\n"
                "3. Set GROQ_API_KEY in .env file"
            )

        self.base_url = "https://api.groq.com/openai/v1/chat/completions"
        self.default_model = "llama-3.1-8b-instant"  # Fast and accurate

        # Test connection
        try:
            # Use a lightweight test call to check connectivity
            self._test_connection()
        except Exception as e:
            print(f"⚠️ Groq API test connection failed: {e}")
            print("   Will fall back to heuristic scoring if needed")

    def _test_connection(self):
        """Test if API key is valid with a tiny call"""
        try:
            resp = self._call("Hello", max_tokens=5, max_retries=1)
            if resp is None:
                raise RuntimeError("No response from Groq test call")
            print(f"✅ Groq API connected successfully (model: {self.default_model})")
        except Exception as e:
            raise

    def _call(
        self,
        prompt: str,
        model: Optional[str] = None,
        temperature: float = 0.3,
        max_tokens: int = 200,
        max_retries: int = 3,
    ) -> str:
        """
        Call Groq API with automatic retry on connection errors

        Args:
            prompt: Input prompt
            model: Model name (default: llama-3.1-8b-instant)
            temperature: Creativity (0.0-1.0)
            max_tokens: Max response length
            max_retries: Number of retry attempts (default: 3)

        Returns:
            Model response text
        """
        headers = {
            "Authorization": f"Bearer {self.api_key}",
            "Content-Type": "application/json",
        }

        payload = {
            "model": model or self.default_model,
            "messages": [{"role": "user", "content": prompt}],
            "temperature": temperature,
            "max_tokens": max_tokens,
        }

        for attempt in range(max_retries):
            try:
                response = requests.post(
                    self.base_url, headers=headers, json=payload, timeout=30
                )

                if response.status_code == 200:
                    data = response.json()
                    # Defensive access
                    try:
                        return data["choices"][0]["message"]["content"]
                    except Exception:
                        return data.get("choices", [{}])[0].get("message", {}).get("content", "")

                elif response.status_code == 429:
                    # Rate limit exceeded - wait and retry
                    wait_time = min(2 ** attempt, 5)
                    print(f"⚠️ agent rate limit (retrying in {wait_time}s)... ({attempt + 1}/{max_retries})")
                    time.sleep(wait_time)
                    continue

                elif response.status_code == 401:
                    # Invalid API key - don't retry
                    print("❌ agent API key invalid! Check GROQ_API_KEY in .env")
                    return ""

                else:
                    # Other HTTP errors
                    print(f"⚠️ agent API error {response.status_code}: {response.text[:200]}")
                    if attempt < max_retries - 1:
                        time.sleep(1)
                        continue
                    return ""

            except requests.exceptions.Timeout:
                print(f"⚠️ agent API timeout (attempt {attempt + 1}/{max_retries})")
                if attempt < max_retries - 1:
                    time.sleep(1)
                    continue
                return ""

            except requests.exceptions.ConnectionError as e:
                # Connection aborted, remote disconnected, etc.
                print(f"⚠️ agent connection error (attempt {attempt + 1}/{max_retries}): {str(e)[:80]}")
                if attempt < max_retries - 1:
                    wait_time = min(2 ** attempt, 5)
                    print(f"   Retrying in {wait_time}s...")
                    time.sleep(wait_time)
                    continue
                return ""

            except Exception as e:
                print(f"⚠️ agent API call failed (attempt {attempt + 1}/{max_retries}): {str(e)[:100]}")
                if attempt < max_retries - 1:
                    time.sleep(1)
                    continue
                return ""

        print(f"❌ agent API failed after {max_retries} retries, using fallback scoring")
        return ""

    def __call__(self, prompt: str) -> str:
        """
        Make callable like gemini_call()

        Usage:
            groq = GroqAPI()
            response = groq("What is 2+2?")
        """
        return self._call(prompt)


# Global instance for easy import
_groq_instance = None


def groq_call(prompt: str) -> str:
    """
    Simple function interface (like gemini_call)
    """
    global _groq_instance

    if _groq_instance is None:
        try:
            _groq_instance = GroqAPI()
        except ValueError as e:
            # No API key configured
            print(f"⚠️ {e}")
            return ""

    return _groq_instance(prompt)
