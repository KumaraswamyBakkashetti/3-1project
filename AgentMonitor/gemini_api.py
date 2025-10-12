"""
Gemini API Wrapper - Google Generative AI Interface
"""
import google.generativeai as genai
import os
from dotenv import load_dotenv

# Load environment variables
load_dotenv()

# Configure Gemini (try both GOOGLE_API_KEY and GEMINI_API_KEY)
GEMINI_API_KEY = os.getenv('GEMINI_API_KEY') or os.getenv('GOOGLE_API_KEY')
if not GEMINI_API_KEY:
    raise ValueError("GEMINI_API_KEY or GOOGLE_API_KEY not found in environment variables. Please set it in .env file")

genai.configure(api_key=GEMINI_API_KEY)

# Create model instance (use gemini-2.0-flash - fast and efficient)
model = genai.GenerativeModel('gemini-2.0-flash')

def call_gemini(prompt):
    """
    Call Gemini API with a prompt and return the response.
    
    Args:
        prompt (str): The prompt to send to Gemini
        
    Returns:
        str: The generated response
    """
    try:
        response = model.generate_content(prompt)
        return response.text
    except Exception as e:
        return f"Error calling Gemini: {str(e)}"

# Keep backward compatibility
llama_call = call_gemini

