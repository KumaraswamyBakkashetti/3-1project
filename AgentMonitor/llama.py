"""
LLM API wrapper - Using Llama via Ollama
"""
import requests
import os
from dotenv import load_dotenv

# Load environment variables
load_dotenv()

# Ollama configuration
OLLAMA_BASE_URL = os.getenv('OLLAMA_BASE_URL', 'https://k7xc1qwz-11434.inc1.devtunnels.ms/')
LLAMA_MODEL = os.getenv('LLAMA_MODEL', 'qwen3:8b')  # Default to qwen3:8b

def llama_call(prompt, model=None):
    """
    Call Llama via Ollama API with a prompt and return the response.
    
    Args:
        prompt (str): The prompt to send to Llama
        model (str): Model to use (default: from env or llama3.2)
        
    Returns:
        str: The generated response
    """
    if model is None:
        model = LLAMA_MODEL
    
    try:
        # Ollama API endpoint
        url = f"{OLLAMA_BASE_URL}/api/generate"
        
        payload = {
            "model": model,
            "prompt": prompt,
            "stream": False,
            "options": {
                "temperature": 0.7,  # Better creativity for code generation
                "num_predict": 2048   # Enough tokens for complete code
            }
        }
        
        response = requests.post(url, json=payload, timeout=120)  # More time for longer responses
        response.raise_for_status()
        
        result = response.json()
        return result.get('response', '').strip()
        
    except requests.exceptions.ConnectionError:
        return "Error: Cannot connect to Ollama. Please make sure Ollama is running (ollama serve)"
    except requests.exceptions.Timeout:
        return "Error: Ollama request timed out. The model might be too slow or not loaded."
    except Exception as e:
        return f"Error calling Llama: {str(e)}"

