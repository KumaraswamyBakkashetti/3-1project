# AgentMonitor/groq_api.py
"""
Groq API Wrapper - 100% FREE API for LLM judging/scoring

Groq provides FREE ultra-fast inference with generous limits:
- 30 requests per minute
- No credit card required
- Models: Llama 3.1, Mixtral, Gemma

Perfect for code scoring and enhancement feedback!
"""

import os
import requests
from typing import Optional
from pathlib import Path
from dotenv import load_dotenv

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


class GroqAPI:
    """
    Groq API wrapper for FREE LLM inference
    
    Sign up: https://console.groq.com
    Get API key: https://console.groq.com/keys
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
        self._test_connection()
    
    def _test_connection(self):
        """Test if API key is valid"""
        try:
            response = self._call("Test", max_tokens=5)
            print(f"✅ Groq API connected successfully (model: {self.default_model})")
        except Exception as e:
            print(f"⚠️ Groq API connection failed: {e}")
            print("   Will fall back to heuristic scoring if needed")
    
    def _call(
        self, 
        prompt: str, 
        model: Optional[str] = None,
        temperature: float = 0.3,
        max_tokens: int = 200,
        max_retries: int = 3
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
        import time
        
        headers = {
            "Authorization": f"Bearer {self.api_key}",
            "Content-Type": "application/json"
        }
        
        payload = {
            "model": model or self.default_model,
            "messages": [{"role": "user", "content": prompt}],
            "temperature": temperature,
            "max_tokens": max_tokens
        }
        
        for attempt in range(max_retries):
            try:
                response = requests.post(
                    self.base_url,
                    headers=headers,
                    json=payload,
                    timeout=30
                )
                
                if response.status_code == 200:
                    return response.json()["choices"][0]["message"]["content"]
                elif response.status_code == 429:
                    # Rate limit exceeded - wait and retry
                    wait_time = min(2 ** attempt, 5)
                    print(f"⚠️ Groq rate limit (30 req/min), retrying in {wait_time}s... ({attempt+1}/{max_retries})")
                    time.sleep(wait_time)
                    continue
                elif response.status_code == 401:
                    # Invalid API key - don't retry
                    print("❌ Groq API key invalid! Check GROQ_API_KEY in .env")
                    return ""
                else:
                    print(f"⚠️ Groq API error {response.status_code}: {response.text[:100]}")
                    if attempt < max_retries - 1:
                        time.sleep(1)
                        continue
                    return ""
                    
            except requests.exceptions.Timeout:
                print(f"⚠️ Groq API timeout (attempt {attempt+1}/{max_retries})")
                if attempt < max_retries - 1:
                    time.sleep(1)
                    continue
                return ""
            except requests.exceptions.ConnectionError as e:
                # Connection aborted, remote disconnected, etc.
                print(f"⚠️ Groq connection error (attempt {attempt+1}/{max_retries}): {str(e)[:80]}")
                if attempt < max_retries - 1:
                    wait_time = min(2 ** attempt, 5)
                    print(f"   Retrying in {wait_time}s...")
                    time.sleep(wait_time)
                    continue
                return ""
            except Exception as e:
                print(f"⚠️ Groq API call failed (attempt {attempt+1}/{max_retries}): {str(e)[:100]}")
                if attempt < max_retries - 1:
                    time.sleep(1)
                    continue
                return ""
        
        print(f"❌ Groq API failed after {max_retries} retries, using fallback scoring")
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
    
    Usage:
        from AgentMonitor.groq_api import groq_call
        score = groq_call("Rate this code: def add(a,b): return a+b")
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
