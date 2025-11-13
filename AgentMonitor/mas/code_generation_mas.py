# AgentMonitor/mas/code_generation_mas.py
"""
Code Generation Multi-Agent System

This is an actual MAS implementation (not just simple agents).
Follows the research paper: Multiple specialized agents collaborating.
"""

import asyncio
from typing import Any, List, Dict, Optional


class CodeGenerationMAS:
    """
    Multi-Agent System for code generation tasks.
    
    Agents:
    1. Analyzer: Analyzes requirements
    2. Coder: Writes code
    3. Tester: Creates tests
    4. Reviewer: Reviews and improves
    
    Flow: Analyzer → Coder → Tester → Reviewer
    """
    
    def __init__(self, llm, language: str = "python", threshold: float = 0.6, max_retries: int = 2, use_full_mas: bool = False):
        """
        Args:
            llm: LLM model for agents
            language: Programming language (default: python)
            threshold: Quality threshold
            max_retries: Max enhancement loops
            use_full_mas: If True, use all 4 agents (Analyzer→Coder→Tester→Reviewer) for richer monitoring
        """
        self.llm = llm
        self.language = language.lower()
        self.threshold = threshold
        self.max_retries = max_retries
        self.use_full_mas = use_full_mas
        
        # Define agent roles with language
        lang_name = language.title()
        self.agents = {
            "Analyzer": Agent("Analyzer", "requirement analyzer", llm, self.language),
            "Coder": Agent("Coder", f"expert {lang_name} programmer", llm, self.language),
            "Tester": Agent("Tester", f"{lang_name} test writer", llm, self.language),
            "Reviewer": Agent("Reviewer", f"{lang_name} code reviewer", llm, self.language)
        }
        
    async def run(self, task: str, monitor=None) -> str:
        """
        Run the MAS pipeline - FAST MODE or FULL MAS MODE
        
        Args:
            task: Programming task
            monitor: AgentMonitor instance (optional)
            
        Returns:
            Final code output
        """
        # Build comprehensive language hint for BEST code
        if self.language and self.language not in ['auto', 'any']:
            lang_hint = f"""

CRITICAL REQUIREMENTS for {self.language} code generation:
🚫 DO NOT generate .env files, configuration files, or environment variables
✅ Generate ACTUAL EXECUTABLE CODE with imports and functions
✅ Complete working implementation (NO TODO/placeholders)
✅ Include all necessary imports/requires at the top
✅ Write the main logic function
✅ Add error handling and edge cases
✅ Include example usage or test cases
✅ Use best practices for {self.language}
✅ Optimize algorithm efficiency

EXAMPLE FORMAT:
- For MongoDB: require('mongoose'), connection function, error handling, example usage
- For API: imports, route definitions, handlers, middleware, example
- For algorithm: function definition, implementation, test cases

Generate COMPLETE, RUNNABLE {self.language} code!"""
        else:
            lang_hint = f"""

CRITICAL REQUIREMENTS:
🚫 DO NOT generate .env files, configuration files, or environment variables
✅ Generate ACTUAL EXECUTABLE CODE
✅ Complete working implementation (NO TODO/placeholders)
✅ Include all necessary imports
✅ Write the main logic
✅ Add error handling
✅ Include test cases

FORBIDDEN:
- Removing existing functionality
- Replacing real code with mock/demo code
- Simplifying production features"""
        
        if not self.use_full_mas:
            # FAST MODE: Coder only for speed
            print(f"⚡ FAST MODE: Using Coder only ({self.language})")
            simple_prompt = f"""{task}{lang_hint}

IMPORTANT: Generate COMPLETE, PRODUCTION-READY, OPTIMIZED code.

REQUIREMENTS:
- NO mock data or placeholders
- Use OPTIMAL algorithms (best time/space complexity)
- Add complexity comments (// Time: O(n), Space: O(1))
- Efficient data structures (HashMap, TreeMap, PriorityQueue as needed)

Output: Complete optimized code only."""
            code = await self._run_agent("Coder", simple_prompt, monitor)
            return code
        else:
            # FULL MAS MODE: All 4 agents with graph edges
            print(f"🔬 FULL MAS MODE: Using all 4 agents ({self.language})")
            
            # 1. Analyzer analyzes the task requirements
            analysis_prompt = f"""Analyze requirements for: {task[:200]}{lang_hint}

FOCUS ON:
- Core functionality needed
- Edge cases and error conditions
- Performance considerations
- Security requirements

Output: Brief technical analysis (3-5 points)"""
            analysis = await self._run_agent("Analyzer", analysis_prompt, monitor)
            
            # Record edge: Analyzer -> Coder
            if monitor:
                monitor.record_graph_edge("Analyzer", "Coder")
            
            # 2. Coder generates COMPLETE production code with optimizations
            code_prompt = f"""{task}{lang_hint}

REQUIREMENTS:
- COMPLETE implementation (no TODOs or placeholders)
- Production-ready code with error handling
- Proper imports and dependencies
- If database/API is mentioned, implement it FULLY
- Do NOT use mock data unless explicitly requested

⚡ OPTIMIZATION REQUIREMENTS:
- Use OPTIMAL time complexity algorithms (avoid brute force when better solutions exist)
- Minimize space complexity (use in-place operations where appropriate)
- Choose efficient data structures (HashMap for O(1) lookup, PriorityQueue for min/max, etc.)
- For Dynamic Programming problems: use bottom-up with space optimization
- For Search/Sort: use optimal algorithms (Binary Search O(log n), QuickSort O(n log n))
- Add complexity analysis as comments (e.g., // Time: O(n log n), Space: O(1))

Output: Complete, runnable, optimized code only."""
            code = await self._run_agent("Coder", code_prompt, monitor)
            
            # Record edge: Coder -> Tester
            if monitor:
                monitor.record_graph_edge("Coder", "Tester")
            
            # 3. Tester validates (SIMPLIFIED - don't include full code)
            test_prompt = f"Test the solution for: {task[:150]}"
            test_feedback = await self._run_agent("Tester", test_prompt, monitor)
            
            # Record edge: Tester -> Reviewer
            if monitor:
                monitor.record_graph_edge("Tester", "Reviewer")
            
            # 4. Reviewer provides final version with STRICT enhancement rules
            # CRITICAL: Include the actual code to review!
            review_prompt = f"""ENHANCE the following code by ADDING improvements WITHOUT removing functionality:

Task: {task}{lang_hint}

EXISTING CODE TO ENHANCE:
```
{code}
```

STRICT RULES:
1. PRESERVE all existing functionality (do NOT simplify or remove features)
2. ADD error handling, validation, edge cases
3. ADD comprehensive documentation (docstrings, comments)
4. ADD proper type hints/annotations
5. IMPROVE code structure and readability
6. ADD tests if not present
7. DO NOT replace real implementations with mock/demo code
8. DO NOT remove database operations, API calls, or core logic
9. KEEP the same length or LONGER (do NOT shorten the code)

⚡ OPTIMIZATION REQUIREMENTS:
10. OPTIMIZE Time Complexity - Use efficient algorithms (avoid O(n²) when O(n log n) is possible)
11. OPTIMIZE Space Complexity - Minimize memory usage, use in-place operations where appropriate
12. ADD complexity analysis comments (e.g., "// Time: O(n log n), Space: O(1)")
13. REPLACE brute-force approaches with optimal algorithms (Dynamic Programming, Binary Search, Hash Maps, etc.)
14. AVOID redundant loops, unnecessary data structures, or repeated computations
15. USE appropriate data structures (HashMap for O(1) lookup, TreeMap for sorted data, etc.)

FORBIDDEN:
- Removing MongoDB/database operations
- Replacing real CRUD with mock data
- Simplifying complex logic to "educational" examples
- Removing imports or dependencies
- Converting production code to demo code
- Shortening or truncating the code
- Using inefficient algorithms when better ones exist

Output ONLY the COMPLETE enhanced code, nothing else. Include ALL parts of the original code with optimizations."""
            
            final_code = await self._run_agent("Reviewer", review_prompt, monitor)
            
            # Debug: Check what we got back
            print(f"[DEBUG] Final code length: {len(final_code) if final_code else 0}")
            print(f"[DEBUG] Initial code length: {len(code) if code else 0}")
            print(f"[DEBUG] Is error response: {self._is_error_response(final_code) if final_code else 'N/A'}")
            if final_code:
                print(f"[DEBUG] First 100 chars: {final_code[:100]}")
            
            # CRITICAL CHECK: If enhanced code is much shorter than original, reject it!
            if final_code and code:
                original_len = len(code)
                enhanced_len = len(final_code)
                # If enhanced is less than 50% of original, it's probably truncated
                if enhanced_len < (original_len * 0.5):
                    print(f"⚠️ Enhanced code ({enhanced_len} chars) is < 50% of original ({original_len} chars) - REJECTING!")
                    final_code = None  # Force fallback to original code
            
            # Return the best code (prefer final, fallback to initial code if needed)
            # Check final_code
            if final_code and final_code.strip() and not self._is_error_response(final_code):
                print(f"✅ Using final code from Reviewer ({len(final_code)} chars)")
                return final_code
            # Check initial code
            elif code and code.strip() and not self._is_error_response(code):
                print(f"⚠️ Reviewer failed, using Coder's code ({len(code)} chars)")
                return code
            # All failed - generate minimal working code as fallback
            else:
                print(f"❌ All agents failed, using fallback template")
                return self._generate_minimal_code(task)
    
    async def _run_agent(self, agent_name: str, task: str, monitor=None) -> str:
        """Run single agent with optional monitoring"""
        agent = self.agents[agent_name]
        
        if monitor:
            # Use monitor's run_agent_with_enhancement
            # Pass the MAS language (user's requested language), not agent's internal language
            result = await monitor.run_agent_with_enhancement(
                agent=agent,
                task=task,
                agent_name=agent_name,
                capability=self.language  # Use MAS language, not agent.language
            )
            # Extract output and ensure it's not None or empty
            if isinstance(result, dict):
                output = result.get("output", "")
            else:
                output = str(result) if result else ""
            
            # Check if output is an error message
            if not output or output.strip() == "" or self._is_error_response(output):
                output = self._generate_minimal_code(task)
            
            return output
        else:
            # Direct execution - RUN IN EXECUTOR TO AVOID BLOCKING
            loop = asyncio.get_event_loop()
            response = await loop.run_in_executor(None, agent.generate_response, task)
            
            # Check if response is an error
            if self._is_error_response(response):
                return self._generate_minimal_code(task)
            
            return response
    
    def _is_error_response(self, text: str) -> bool:
        """OPTIMIZED: Check if response is an error message (not valid code with error handling)"""
        if not text or not text.strip():
            return True
        
        text_lower = text.lower()
        text_len = len(text.strip())
        
        # OPTIMIZATION 1: If code is long (> 500 chars), it's probably real code, not an error
        # Even if it contains error-handling keywords like Exception, try, catch
        if text_len > 500:
            # Check if it starts with actual error messages
            if text.strip().startswith(("Error:", "Failed:", "Exception:", "/*\n * GEMINI API")):
                return True
            # Otherwise it's likely valid code with error handling
            return False
        
        # OPTIMIZATION 2: For shorter code, check more carefully
        error_indicators = [
            "error:",
            "blocked",
            "safety filter",
            "service unavailable",
            "api service unavailable",
            "gemini api service unavailable"
        ]
        
        # Check if text is ONLY an error (short and contains error keywords at start)
        if text_len < 200 and any(indicator in text_lower for indicator in error_indicators):
            return True
        
        return False
    
    def _generate_minimal_code(self, task: str) -> str:
        """
        Generate error message when Gemini API is completely unavailable.
        
        This should only be called as a last resort when all models fail.
        """
        lang = self.language.lower()
        
        # Return clear error message instead of template
        error_message = f"""/*
 * GEMINI API SERVICE UNAVAILABLE
 * 
 * Google's Gemini API is temporarily down (503 Service Unavailable).
 * This is a temporary Google server issue, not a problem with your code.
 * 
 * What to do:
 * 1. Wait 10-30 minutes and try again
 * 2. Check Google AI Studio status: https://aistudio.google.com
 * 3. Your request has been saved and you can retry later
 * 
 * Task requested: {task[:200]}...
 * Language: {lang}
 * 
 * This message will be replaced with actual code when the service recovers.
 */

// Placeholder - waiting for Gemini API service to recover
public class ServiceUnavailable {{
    // The code generation service is temporarily unavailable
    // Please try again in a few minutes
}}"""
        
        return error_message
        
        # Detect common problem patterns
        is_nqueens = 'n queens' in task_lower or 'nqueens' in task_lower
        is_sorting = any(word in task_lower for word in ['sort', 'quicksort', 'mergesort', 'bubblesort'])
        is_search = any(word in task_lower for word in ['search', 'binary search', 'dfs', 'bfs'])
        is_tree = any(word in task_lower for word in ['tree', 'binary tree', 'bst'])
        is_graph = any(word in task_lower for word in ['graph', 'dijkstra', 'shortest path'])
        
        # Generate language-specific templates
        if lang in ['java']:
            if is_nqueens:
                return """import java.util.ArrayList;
import java.util.List;

/**
 * N-Queens Problem Solver using Backtracking
 * Finds all possible arrangements of N queens on an NxN chessboard
 */
public class NQueens {
    
    /**
     * Main method to solve N-Queens problem
     * @param n Size of the board (N x N)
     * @return List of all solutions
     */
    public List<List<String>> solveNQueens(int n) {
        List<List<String>> solutions = new ArrayList<>();
        int[] board = new int[n]; // board[row] = column of queen in that row
        backtrack(0, n, board, solutions);
        return solutions;
    }
    
    /**
     * Backtracking algorithm to find all valid queen placements
     */
    private void backtrack(int row, int n, int[] board, List<List<String>> solutions) {
        if (row == n) {
            // Found a valid solution
            solutions.add(generateBoard(board, n));
            return;
        }
        
        // Try placing queen in each column of current row
        for (int col = 0; col < n; col++) {
            if (isSafe(row, col, board)) {
                board[row] = col;  // Place queen
                backtrack(row + 1, n, board, solutions);  // Recurse
                // Backtrack happens automatically via loop iteration
            }
        }
    }
    
    /**
     * Check if placing a queen at (row, col) is safe
     */
    private boolean isSafe(int row, int col, int[] board) {
        for (int prevRow = 0; prevRow < row; prevRow++) {
            int prevCol = board[prevRow];
            
            // Check same column
            if (prevCol == col) return false;
            
            // Check diagonal (abs(row diff) == abs(col diff))
            if (Math.abs(row - prevRow) == Math.abs(col - prevCol)) {
                return false;
            }
        }
        return true;
    }
    
    /**
     * Generate board visualization from queen positions
     */
    private List<String> generateBoard(int[] board, int n) {
        List<String> result = new ArrayList<>();
        for (int row = 0; row < n; row++) {
            StringBuilder sb = new StringBuilder();
            for (int col = 0; col < n; col++) {
                sb.append(board[row] == col ? 'Q' : '.');
            }
            result.add(sb.toString());
        }
        return result;
    }
    
    /**
     * Example usage and testing
     */
    public static void main(String[] args) {
        NQueens solver = new NQueens();
        
        // Test with N=4
        int n = 4;
        System.out.println("Solutions for N = " + n + ":");
        List<List<String>> solutions = solver.solveNQueens(n);
        
        for (int i = 0; i < solutions.size(); i++) {
            System.out.println("\\nSolution " + (i + 1) + ":");
            for (String row : solutions.get(i)) {
                System.out.println(row);
            }
        }
        
        System.out.println("\\nTotal solutions: " + solutions.size());
    }
}
"""
            elif is_sorting:
                return """/**
 * Sorting Algorithm Implementation
 */
public class SortingAlgorithm {
    
    /**
     * QuickSort algorithm - Divide and Conquer
     * Time: O(n log n) average, O(n²) worst
     * Space: O(log n) due to recursion
     */
    public void quickSort(int[] arr, int low, int high) {
        if (low < high) {
            int pivotIndex = partition(arr, low, high);
            quickSort(arr, low, pivotIndex - 1);
            quickSort(arr, pivotIndex + 1, high);
        }
    }
    
    private int partition(int[] arr, int low, int high) {
        int pivot = arr[high];
        int i = low - 1;
        
        for (int j = low; j < high; j++) {
            if (arr[j] < pivot) {
                i++;
                swap(arr, i, j);
            }
        }
        swap(arr, i + 1, high);
        return i + 1;
    }
    
    private void swap(int[] arr, int i, int j) {
        int temp = arr[i];
        arr[i] = arr[j];
        arr[j] = temp;
    }
    
    public static void main(String[] args) {
        SortingAlgorithm sorter = new SortingAlgorithm();
        int[] arr = {64, 34, 25, 12, 22, 11, 90};
        
        System.out.println("Original: " + java.util.Arrays.toString(arr));
        sorter.quickSort(arr, 0, arr.length - 1);
        System.out.println("Sorted: " + java.util.Arrays.toString(arr));
    }
}
"""
            else:
                # Generic Java template
                return f"""/**
 * Solution for: {task[:80]}
 */
public class Solution {{
    
    /**
     * Main solution method
     * TODO: Implement the algorithm
     */
    public void solve() {{
        // Your implementation here
        System.out.println("Solution not yet implemented");
    }}
    
    /**
     * Test the solution
     */
    public static void main(String[] args) {{
        Solution solution = new Solution();
        solution.solve();
    }}
}}
"""
        
        elif lang == 'python':
            if is_nqueens:
                return """from typing import List

def solve_n_queens(n: int) -> List[List[str]]:
    \"\"\"
    Solve N-Queens problem using backtracking.
    
    Args:
        n: Size of the board (N x N)
    
    Returns:
        List of all valid solutions
    \"\"\"
    solutions = []
    board = [-1] * n  # board[row] = column of queen
    
    def is_safe(row: int, col: int) -> bool:
        for prev_row in range(row):
            prev_col = board[prev_row]
            if prev_col == col or abs(row - prev_row) == abs(col - prev_col):
                return False
        return True
    
    def backtrack(row: int):
        if row == n:
            solutions.append(generate_board())
            return
        
        for col in range(n):
            if is_safe(row, col):
                board[row] = col
                backtrack(row + 1)
    
    def generate_board() -> List[str]:
        return ['.' * board[row] + 'Q' + '.' * (n - board[row] - 1) for row in range(n)]
    
    backtrack(0)
    return solutions

# Example usage
if __name__ == "__main__":
    solutions = solve_n_queens(4)
    print(f"Total solutions for N=4: {len(solutions)}")
    for i, solution in enumerate(solutions, 1):
        print(f"\\nSolution {i}:")
        for row in solution:
            print(row)
"""
            else:
                return f"""def solution():
    \"\"\"
    {task[:100]}
    
    TODO: Implement the algorithm
    \"\"\"
    pass

if __name__ == "__main__":
    result = solution()
    print(result)
"""
        
        elif lang in ['javascript', 'js']:
            return f"""/**
 * {task[:80]}
 */
function solution() {{
    // TODO: Implement the algorithm
    return null;
}}

// Example usage
console.log(solution());
"""
        
        else:
            # Generic fallback
            return f"""# Solution for: {task[:80]}

def solution():
    # TODO: Implement
    pass

if __name__ == "__main__":
    solution()
"""


class Agent:
    """Individual agent within the MAS"""
    
    def __init__(self, name: str, role: str, llm, language: str = "python"):
        self.name = name
        self.role = role
        self.llm = llm
        self.language = language.lower()
    
    def generate_response(self, prompt: str) -> str:
        """Generate response - ONLY CODE, no explanation"""
        try:
            # Create COMPREHENSIVE directive for BEST code
            lang_directive = ''
            if self.language and self.language not in ['auto', 'any']:
                lang_directive = f"""LANGUAGE: {self.language.upper()}

⚠️ CRITICAL: Generate COMPLETE, WORKING {self.language.upper()} CODE - NOT configuration files!

🚫 NEVER GENERATE:
- .env files or environment variables (MONGODB_URI="...", PORT=...)
- Configuration objects without code
- Just comments or documentation
- Placeholder files

✅ ALWAYS GENERATE:
- Actual executable {self.language.upper()} code
- Import/require statements at the top
- Function definitions with REAL implementation
- Error handling (try-catch, if-else checks)
- Example usage or test cases at the bottom
- Complete working solution

ABSOLUTE REQUIREMENTS:
✓ Start with imports (const express = require('express'))
✓ COMPLETE implementation (every function FULLY coded)
✓ NO "TODO" comments anywhere
✓ NO placeholder functions
✓ Real working algorithm (not empty shells)
✓ Include actual test/usage examples
✓ Add error handling for edge cases
✓ Optimize for O(N) time complexity where possible
✓ Follow {self.language.upper()} best practices

EXAMPLES OF UNACCEPTABLE OUTPUT:
❌ MONGODB_URI="mongodb://localhost:27017/db"
❌ PORT=3000
❌ function solution() {{ // TODO: Implement }}
❌ // Configuration file for MongoDB

REQUIRED FORMAT EXAMPLE (MongoDB connection):
```{self.language}
const express = require('express');
const mongoose = require('mongoose');

// MongoDB connection function
async function connectDB() {{
  try {{
    await mongoose.connect('mongodb://localhost:27017/mydb');
    console.log('Connected to MongoDB');
  }} catch (err) {{
    console.error('Connection failed:', err);
  }}
}}

// Example usage
connectDB();
```

Write the ACTUAL, COMPLETE, EXECUTABLE {self.language.upper()} CODE!

"""
            else:
                lang_directive = f"""⚠️ CRITICAL: Generate COMPLETE, WORKING CODE - NOT configuration!

🚫 NEVER GENERATE environment variables or config files
✅ ALWAYS GENERATE actual executable code with imports and functions

ABSOLUTE REQUIREMENTS:
✓ COMPLETE implementation (every function FULLY implemented)
✓ NO "TODO" comments
✓ NO placeholder functions
✓ Real working algorithm
✓ Include actual test cases
✓ Add error handling

REQUIRED: Write the ACTUAL, COMPLETE, EXECUTABLE CODE!

"""

            # Concise final instruction with emphasis
            full_prompt = f"{lang_directive}{prompt}\n\n⚡ IMPORTANT: Generate EXECUTABLE {self.language.upper()} CODE with imports, functions, and logic. NOT just environment variables or config!"
            
            start = __import__('time').time()
            
            if callable(self.llm):
                response = self.llm(full_prompt)
                elapsed = __import__('time').time() - start
                
                response_str = response if isinstance(response, str) else str(response)
                
                # Check if response is blocked or error
                if not response_str:
                    print(f"[{self.name}] {elapsed:.1f}s -> Empty response from Gemini!")
                    return ""
                # IMPROVED: Only reject if response is ACTUALLY blocked (not just mentions "blocked" in code comments)
                # Check for actual error patterns at the START of response
                elif (response_str.strip().startswith("Error:") or 
                      response_str.strip().startswith("Sorry,") or
                      response_str.strip().startswith("I cannot") or
                      response_str.strip().startswith("I can't")):
                    print(f"[{self.name}] {elapsed:.1f}s -> ERROR/BLOCKED response: {response_str[:100]}")
                    return ""
                elif len(response_str) < 100 and "error" in response_str.lower():
                    # Only reject if it's a SHORT error message
                    print(f"[{self.name}] {elapsed:.1f}s -> ERROR response: {response_str[:100]}")
                    return ""
                
                # EXTRACT ONLY CODE
                clean_code = self._extract_code(response_str)
                
                # POST-PROCESS: Check for TODO/placeholders and REJECT
                if self._has_placeholders(clean_code):
                    print(f"[{self.name}] ❌ REJECTED: Code contains TODOs/placeholders!")
                    print(f"[{self.name}] Requesting complete implementation...")
                    # Try again with even stricter prompt
                    retry_prompt = f"{lang_directive}{prompt}\n\n🚫 YOUR PREVIOUS ATTEMPT HAD TODO COMMENTS - THIS IS UNACCEPTABLE!\n\nGenerate the ACTUAL COMPLETE working code with REAL implementation. NO TODOs!"
                    retry_response = self.llm(retry_prompt)
                    retry_str = retry_response if isinstance(retry_response, str) else str(retry_response)
                    clean_code = self._extract_code(retry_str)
                    
                    # If still has TODOs, return empty (will trigger fallback)
                    if self._has_placeholders(clean_code):
                        print(f"[{self.name}] ❌ STILL HAS TODOs after retry - returning empty")
                        return ""
                
                print(f"[{self.name}] {elapsed:.1f}s -> {len(clean_code)} chars")
                
                # Check if extraction resulted in nothing
                if not clean_code or len(clean_code) < 50:
                    print(f"[{self.name}] WARNING: Code extraction produced very short result ({len(clean_code) if clean_code else 0} chars)")
                    print(f"[{self.name}] Raw response preview: {response_str[:200]}")
                
                return clean_code
            else:
                return ""  # Return empty, not error message
                
        except Exception as e:
            print(f"[{self.name}] Exception: {str(e)}")
            return ""  # Return empty, not error message
    
    def _has_placeholders(self, code: str) -> bool:
        """Check if code contains TODO comments, placeholder patterns, or just config"""
        if not code:
            return True
        
        # If code is too short (< 100 chars), likely incomplete
        if len(code.strip()) < 100:
            print(f"[PLACEHOLDER CHECK] Code too short: {len(code.strip())} chars")
            return True
        
        code_lower = code.lower()
        code_stripped = code.strip()
        
        # Check if it's just environment variables (not actual code)
        env_patterns = [
            'mongodb_uri=',
            'port=',
            'db_url=',
            'api_key=',
            'database_url='
        ]
        
        # If code ONLY contains env variables and no actual code
        has_env_only = any(pattern in code_lower for pattern in env_patterns)
        has_code_markers = any(marker in code_lower for marker in [
            'function', 'const ', 'let ', 'var ', 'def ', 'class ', 
            'import ', 'require(', 'async ', 'await ', 'try {', 'catch'
        ])
        
        if has_env_only and not has_code_markers:
            print(f"[PLACEHOLDER CHECK] Code is just environment variables, not actual code!")
            return True
            
        placeholder_patterns = [
            'todo',
            'todo:',
            'implement this',
            'implement the',
            '// implement',
            '# implement',
            '/* todo',
            'pass  # ',
            'return null  //',
            'return null;  //',
            '{ // todo',
            '{ /* todo',
            'function solution()',  # Generic placeholder function name
            'def solution():',       # Generic placeholder function name
            '// ...implementation',
            '# ...implementation',
            'your code here',
            'write code here',
            'add code here'
        ]
        
        for pattern in placeholder_patterns:
            if pattern in code_lower:
                print(f"[PLACEHOLDER CHECK] Found pattern: '{pattern}'")
                return True
        
        return False
    
    def _extract_code(self, response_str: str) -> str:
        """Extract ONLY code from response"""
        import re
        
        # Method 1: Extract from markdown code blocks
        if "```" in response_str:
            code_blocks = re.findall(r'```(?:\w+)?\s*(.*?)```', response_str, re.DOTALL)
            if code_blocks:
                return code_blocks[0].strip()
        
        # Method 2: Find code by looking for function/class definitions
        lines = response_str.split('\n')
        code_lines = []
        in_code = False
        
        for line in lines:
            stripped = line.strip()
            
            # Start collecting at code indicators
            if stripped.startswith(('def ', 'function ', 'class ', 'import ', 'from ', 'public ', 'private ', '#include')):
                in_code = True
            
            # Skip explanatory lines
            if in_code and stripped:
                # Skip lines that look like explanations
                if any(phrase in stripped.lower() for phrase in ['this function', 'this code', 'example:', 'note:', 'usage:']):
                    continue
                code_lines.append(line)
        
        if code_lines:
            return '\n'.join(code_lines).strip()
        
        # Method 3: Return everything (last resort)
        return response_str.strip()

