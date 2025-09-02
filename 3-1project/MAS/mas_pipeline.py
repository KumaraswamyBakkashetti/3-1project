# import os
# import google.generativeai as genai

# # =========================
# # Configure Gemini API
# # =========================
# api_key = os.getenv("GEMINI_API_KEY") or input("Enter your Gemini API key: ")
# genai.configure(api_key=api_key)

# # =========================
# # Agent 1 - Requirement Analyzer
# # =========================
# class RequirementAnalyzer:
#     def run(self, prompt):
#         print("\n[Agent 1] Analyzing requirements...")
#         model = genai.GenerativeModel("gemini-1.5-flash")
#         response = model.generate_content(
#             f"Analyze this programming task and break it into clear requirements:\n{prompt}"
#         )
#         analysis = response.text
#         print("\n--- Analysis ---\n", analysis)
#         return {"prompt": prompt, "analysis": analysis}

# # =========================
# # Agent 2 - Code Generator
# # =========================
# class CodeGenerator:
#     def run(self, data):
#         print("\n[Agent 2] Generating code...")
#         model = genai.GenerativeModel("gemini-1.5-flash")
#         response = model.generate_content(
#             f"Write working {data['prompt']}.\nFollow these requirements:\n{data['analysis']}"
#         )
#         code = response.text
#         print("\n--- Generated Code ---\n", code)
#         data["code"] = code
#         return data

# # =========================
# # Agent 3 - Code Reviewer
# # =========================
# class CodeReviewer:
#     def run(self, data):
#         print("\n[Agent 3] Reviewing code...")
#         model = genai.GenerativeModel("gemini-1.5-flash")
#         response = model.generate_content(
#             f"Review the following code for bugs, inefficiencies, and suggest improvements:\n{data['code']}"
#         )
#         review = response.text
#         print("\n--- Review ---\n", review)
#         data["review"] = review
#         return data

# # =========================
# # Agent 4 - Unit Test Writer
# # =========================
# class UnitTestWriter:
#     def run(self, data):
#         print("\n[Agent 4] Writing unit tests...")
#         model = genai.GenerativeModel("gemini-1.5-flash")
#         response = model.generate_content(
#             f"Write Python unit tests for the following code:\n{data['code']}"
#         )
#         tests = response.text
#         print("\n--- Unit Tests ---\n", tests)
#         data["tests"] = tests
#         return data

# # =========================
# # Agent 5 - Code Executor (Simulated)
# # =========================
# class CodeExecutor:
#     def run(self, data):
#         print("\n[Agent 5] Executing code & running tests (simulation)...")
#         data["execution_results"] = "Simulated: All tests passed."
#         print(data["execution_results"])
#         return data

# # =========================
# # Run MAS Pipeline
# # =========================
# if __name__ == "__main__":
#     user_prompt = input("Enter your coding task: ")

#     pipeline = [
#         RequirementAnalyzer(),
#         CodeGenerator(),
#         CodeReviewer(),
#         UnitTestWriter(),
#         CodeExecutor()
#     ]

#     data = {}
#     data = pipeline[0].run(user_prompt)
#     data = pipeline[1].run(data)
#     data = pipeline[2].run(data)
#     data = pipeline[3].run(data)
#     data = pipeline[4].run(data)

#     print("\n=== Final MAS Output ===")
#     for k, v in data.items():
#         print(f"{k}:\n{v}\n")
# MAS/mas_pipeline.py


# MAS/mas_pipeline.py
"""
MAS pipeline: 5 agents.
Each agent accepts an optional `llm` client (not used by default).
Agents return/append to a shared `data` dict.
This file intentionally does not force any external LLM - it uses simple
fallback/dummy outputs so MAS remains runnable offline.
"""

from typing import Optional, Dict, Any

class RequirementAnalyzer:
    def __init__(self, llm=None):
        self.llm = llm

    def run(self, prompt: str) -> Dict[str, Any]:
        """
        Accepts a prompt string and returns a data dict with at least 'prompt' and 'analysis'.
        """
        print("\n[Agent 1] Analyzing requirements...")
        if self.llm:
            try:
                resp = self.llm.generate_content(f"Analyze and break down this task into requirements:\n{prompt}")
                analysis = resp.strip()
            except Exception:
                analysis = f"Task: {prompt}\nRequirements: Handle basic inputs."
        else:
            analysis = f"Task: {prompt}\nRequirements: Function must handle basic inputs."
        print("Analysis Output:", analysis)
        return {"prompt": prompt, "analysis": analysis}


class CodeGenerator:
    def __init__(self, llm=None):
        self.llm = llm

    def run(self, data: Dict[str, Any]) -> Dict[str, Any]:
        print("\n[Agent 2] Generating code...")
        prompt = data.get("prompt", "")
        if self.llm:
            try:
                resp = self.llm.generate_content(
                    f"Write working code for this task:\n{prompt}\nFollow these requirements:\n{data.get('analysis','')}"
                )
                code = resp.strip()
            except Exception:
                code = f"// Error calling LLM - fallback code placeholder for: {prompt}"
        else:
            # Dummy placeholder (safe, simple)
            code = f"// Dummy code placeholder for: {prompt}\n// Implement merge sort or relevant algorithm here..."
        print("--- Generated Code ---\n", code)
        data["code"] = code
        return data


class CodeReviewer:
    def __init__(self, llm=None):
        self.llm = llm

    def run(self, data: Dict[str, Any]) -> Dict[str, Any]:
        print("\n[Agent 3] Reviewing code...")
        code = data.get("code", "")
        if self.llm:
            try:
                resp = self.llm.generate_content(f"Review the following code and list bugs/inefficiencies:\n{code}")
                review = resp.strip()
            except Exception:
                review = "No review available (LLM call failed)."
        else:
            issues = []
            # very lightweight heuristic reviewer
            if "TODO" in code or "Implement" in code:
                issues.append("Placeholder code present — not implemented.")
            if "print(" in code or "System.out.println" in code:
                issues.append("Uses print statements (may not return values).")
            review = "\n".join(issues) if issues else "No major issues found."
        print("--- Review ---\n", review)
        data["review"] = review
        return data


class UnitTestWriter:
    def __init__(self, llm=None):
        self.llm = llm

    def run(self, data: Dict[str, Any]) -> Dict[str, Any]:
        print("\n[Agent 4] Writing unit tests...")
        code = data.get("code", "")
        if self.llm:
            try:
                resp = self.llm.generate_content(f"Write unit tests for the following code:\n{code}")
                tests = resp.strip()
            except Exception:
                tests = "## Unit tests generation failed (LLM)."
        else:
            # Dummy tests placeholder
            tests = "## Dummy tests: assert True"
        print("--- Unit Tests ---\n", tests)
        data["tests"] = tests
        return data


class CodeExecutor:
    def __init__(self):
        # Execution sandbox intentionally not integrated here for safety.
        pass

    def run(self, data: Dict[str, Any]) -> Dict[str, Any]:
        print("\n[Agent 5] Executing code & running tests (simulation)...")
        # Simulated execution result — replace by a sandboxed runner later if needed.
        data["execution_results"] = {"passed": 1, "failed": 0, "note": "Simulated"}
        print("--- Execution Results ---\n", data["execution_results"])
        return data

