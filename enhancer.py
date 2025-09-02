import time
import google.api_core.exceptions
import google.generativeai as genai

class CodeEnhancer:
    def __init__(self, model_name="gemini-1.5-flash"):
        self.model = genai.GenerativeModel(model_name)

    def improve(self, content):
        """
        Safely call Gemini to improve code.
        Retries if rate limit (429) is hit.
        """
        prompt = (
            "You are a helpful code improver. Improve the following code snippet to fix bugs, "
            "increase correctness, enhance readability, and ensure safety. "
            "Return only the improved code.\n\n"
            f"Code:\n{content}"
        )

        while True:
            try:
                response = self.model.generate_content(prompt)
                return response.text.strip()
            except google.api_core.exceptions.ResourceExhausted:
                print("⚠️ Enhancer hit Gemini quota. Waiting 60s before retrying...")
                time.sleep(60)
