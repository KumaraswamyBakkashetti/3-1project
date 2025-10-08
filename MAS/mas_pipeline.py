# MAS/mas_pipeline.py
"""
Multi-Agent System (MAS) pipelines.
Provides code_pipeline and qa_pipeline.
"""

from typing import Optional, Dict, Any
import subprocess
import tempfile
import os

class RequirementAnalyzer:
    def __init__(self, llm=None):
        self.llm = llm

    def run(self, prompt: str) -> Dict[str, Any]:
        print("\n[Agent 1] Analyzing requirements...")
        if self.llm:
            try:
                resp = self.llm.generate_content(f"Analyze and break down this task into requirements:\n{prompt}")
                analysis = resp.strip()
            except Exception:
                analysis = f"Task: {prompt}\nRequirements: Handle basic inputs."
        else:
            analysis = f"Task: {prompt}\nRequirements: Function must handle basic inputs."
        print("Analysis Output:", (analysis[:300] + "...") if len(analysis) > 300 else analysis)
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
                    f"Write working code for this task:\n{prompt}\nFollow these requirements:\n{data.get('analysis','')}\n\nReturn ONLY the code without markdown formatting or explanations."
                )
                code = resp.strip()
                # Remove markdown code blocks if present
                if code.startswith("```python"):
                    code = code[9:]  # Remove ```python
                elif code.startswith("```"):
                    code = code[3:]  # Remove ```
                if code.endswith("```"):
                    code = code[:-3]  # Remove closing ```
                code = code.strip()
            except Exception:
                code = f"# Error calling LLM - fallback code placeholder for: {prompt}"
        else:
            code = f"# Dummy code placeholder for: {prompt}\n# Implement algorithm here..."
        data["code"] = code

        # Basic language inference
        lower_prompt = (prompt or "").lower()
        if "java" in lower_prompt or "public " in code or "class " in code:
            data["code_language"] = "java"
        elif "python" in lower_prompt or "def " in code or "import " in code:
            data["code_language"] = "python"
        else:
            data["code_language"] = "unknown"
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
            if "TODO" in code or "Implement" in code:
                issues.append("Placeholder code present — not implemented.")
            if "print(" in code or "System.out.println" in code:
                issues.append("Uses print statements (may not return values).")
            review = "\n".join(issues) if issues else "No major issues found."
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
            tests = "## Dummy tests: assert True"
        data["tests"] = tests
        return data


class CodeExecutor:
    def __init__(self):
        pass

    def run(self, data: Dict[str, Any]) -> Dict[str, Any]:
        """
        Attempt to execute code if language is python (syntax check).
        For other languages we simulate.
        """
        print("\n[Agent 5] Executing code & running tests (simulation/attempt)...")
        code = data.get("code", "")
        lang = data.get("code_language", "unknown")

        if lang == "python":
            try:
                with tempfile.TemporaryDirectory() as d:
                    code_file = os.path.join(d, "submission.py")
                    with open(code_file, "w", encoding="utf-8") as f:
                        f.write(code)
                    # Syntax check
                    subprocess.check_output(["python", "-m", "py_compile", code_file], stderr=subprocess.STDOUT, timeout=10)
                data["execution_results"] = {"passed": 1, "failed": 0, "note": "syntax_ok"}
            except subprocess.CalledProcessError as e:
                out = e.output.decode(errors="ignore") if getattr(e, "output", None) else str(e)
                data["execution_results"] = {"passed": 0, "failed": 1, "note": "runtime_or_syntax_error", "output": out}
            except Exception as e:
                data["execution_results"] = {"passed": 0, "failed": 1, "note": f"exec_error:{e}"}
        else:
            data["execution_results"] = {"passed": 1, "failed": 0, "note": "simulated_non_python"}
        print("--- Execution Results ---\n", data["execution_results"])
        return data


# Top-level pipeline constructors
def code_pipeline(llm_client=None):
    return [
        ("RequirementAnalyzer", RequirementAnalyzer(llm=llm_client), "analysis"),
        ("CodeGenerator", CodeGenerator(llm=llm_client), "code"),
        ("CodeReviewer", CodeReviewer(llm=llm_client), "review"),
        ("UnitTestWriter", UnitTestWriter(llm=llm_client), "tests"),
        ("CodeExecutor", CodeExecutor(), "execution_results")
    ]


# QA pipeline for reasoning / QA tasks
class QAAnswerer:
    def __init__(self, llm=None):
        self.llm = llm

    def run(self, prompt: str) -> Dict[str, Any]:
        print("\n[QA Agent] Producing answer text...")
        if self.llm:
            try:
                resp = self.llm.generate_content(f"Answer concisely. QUESTION:\n{prompt}")
                answer = resp.strip()
            except Exception:
                answer = "LLM failure: no answer."
        else:
            answer = "Heuristic answer: unable to compute without LLM."
        return {"prompt": prompt, "answer": answer}


class QAReviewer:
    def __init__(self, llm=None):
        self.llm = llm

    def run(self, data: Dict[str, Any]) -> Dict[str, Any]:
        print("\n[QA Reviewer] Reviewing answer...")
        answer = data.get("answer", "")
        if self.llm:
            try:
                resp = self.llm.generate_content(f"Review this answer and point out issues:\n{answer}")
                review = resp.strip()
            except Exception:
                review = "No review (LLM call failed)."
        else:
            review = "No major issues found (heuristic)."
        data["review"] = review
        return data


def qa_pipeline(llm_client=None):
    return [
        ("RequirementAnalyzer", RequirementAnalyzer(llm=llm_client), "analysis"),
        ("QAAnswerer", QAAnswerer(llm=llm_client), "answer"),
        ("QAReviewer", QAReviewer(llm=llm_client), "review")
    ]
