import time
import google.api_core.exceptions
import google.generativeai as genai

# --- Base Agent with retry-safe call ---
class BaseAgent:
    def __init__(self, model_name="gemini-1.5-flash"):
        self.model = genai.GenerativeModel(model_name)

    def safe_generate(self, prompt):
        """
        Wrapper around Gemini with retry when quota is hit (429).
        """
        while True:
            try:
                response = self.model.generate_content(prompt)
                return response.text.strip()
            except google.api_core.exceptions.ResourceExhausted:
                print("⚠️ Rate limit hit by agent. Waiting 60s before retry...")
                time.sleep(60)


# --- Individual Agents ---
class RequirementAnalyzer(BaseAgent):
    def run(self, prompt):
        print("\n[Agent 1] Analyzing requirements...")
        analysis = self.safe_generate(
            f"Analyze this programming task and break it into clear requirements:\n{prompt}"
        )
        print("\n--- Analysis ---\n", analysis)
        return {"prompt": prompt, "analysis": analysis}


class CodeGenerator(BaseAgent):
    def run(self, data):
        print("\n[Agent 2] Generating code...")
        code = self.safe_generate(
            f"Write working {data['prompt']}.\nFollow these requirements:\n{data['analysis']}"
        )
        print("\n--- Generated Code ---\n", code)
        data["code"] = code
        return data


class CodeReviewer(BaseAgent):
    def run(self, data):
        print("\n[Agent 3] Reviewing code...")
        review = self.safe_generate(
            f"Review the following code for bugs, inefficiencies, and suggest improvements:\n{data['code']}"
        )
        print("\n--- Review ---\n", review)
        data["review"] = review
        return data


class UnitTestWriter(BaseAgent):
    def run(self, data):
        print("\n[Agent 4] Writing unit tests...")
        tests = self.safe_generate(
            f"Write Python unit tests for the following code:\n{data['code']}"
        )
        print("\n--- Unit Tests ---\n", tests)
        data["tests"] = tests
        return data


class CodeExecutor(BaseAgent):
    def run(self, data):
        print("\n[Agent 5] Executing code & running tests (simulation)...")
        # No Gemini call → just simulate to avoid quota waste
        data["execution_results"] = "Simulated: All tests passed."
        print(data["execution_results"])
        return data
