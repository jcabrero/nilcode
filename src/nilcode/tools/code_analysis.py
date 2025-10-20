"""
Code analysis tools for parsing and analyzing code.
These tools help the tester agent validate code quality.
"""

import ast
import re
from pathlib import Path
from typing import List, Dict, Any
from langchain.tools import tool


@tool
def analyze_python_syntax(code: str) -> str:
    """
    Check if Python code has valid syntax.

    Args:
        code: Python code to analyze

    Returns:
        Analysis result with syntax errors if any
    """
    try:
        ast.parse(code)
        return "✅ Python syntax is valid"
    except SyntaxError as e:
        return f"❌ Syntax Error at line {e.lineno}: {e.msg}"
    except Exception as e:
        return f"❌ Error analyzing code: {str(e)}"


@tool
def count_functions(code: str, language: str = "python") -> str:
    """
    Count the number of functions in the code.

    Args:
        code: Code to analyze
        language: Programming language (python, javascript)

    Returns:
        Number of functions found
    """
    try:
        if language == "python":
            tree = ast.parse(code)
            functions = [node for node in ast.walk(tree) if isinstance(node, ast.FunctionDef)]
            classes = [node for node in ast.walk(tree) if isinstance(node, ast.ClassDef)]

            return (
                f"Found {len(functions)} function(s) and {len(classes)} class(es)\n"
                f"Functions: {[f.name for f in functions]}\n"
                f"Classes: {[c.name for c in classes]}"
            )
        elif language == "javascript":
            # Simple regex-based counting for JS
            function_pattern = r"function\s+\w+\s*\(|const\s+\w+\s*=\s*\(.*\)\s*=>|\w+\s*\(.*\)\s*{"
            matches = re.findall(function_pattern, code)
            return f"Found approximately {len(matches)} function(s) in JavaScript code"
        else:
            return f"Language {language} not supported for analysis"
    except Exception as e:
        return f"Error analyzing code: {str(e)}"


@tool
def check_imports(code: str) -> str:
    """
    Extract and list all imports from Python code.

    Args:
        code: Python code to analyze

    Returns:
        List of imports
    """
    try:
        tree = ast.parse(code)
        imports = []

        for node in ast.walk(tree):
            if isinstance(node, ast.Import):
                for alias in node.names:
                    imports.append(alias.name)
            elif isinstance(node, ast.ImportFrom):
                module = node.module or ""
                for alias in node.names:
                    imports.append(f"{module}.{alias.name}")

        if not imports:
            return "No imports found"

        return "Imports:\n" + "\n".join(f"  - {imp}" for imp in imports)
    except Exception as e:
        return f"Error analyzing imports: {str(e)}"


@tool
def find_todos_in_code(code: str) -> str:
    """
    Find TODO, FIXME, and NOTE comments in code.

    Args:
        code: Code to search

    Returns:
        List of found comments
    """
    patterns = [
        r"#\s*(TODO|FIXME|NOTE|HACK|XXX):?\s*(.+)",  # Python, JS single-line
        r"//\s*(TODO|FIXME|NOTE|HACK|XXX):?\s*(.+)",  # JS, C++ single-line
    ]

    comments = []
    for i, line in enumerate(code.split("\n"), 1):
        for pattern in patterns:
            matches = re.finditer(pattern, line, re.IGNORECASE)
            for match in matches:
                comment_type = match.group(1).upper()
                comment_text = match.group(2).strip()
                comments.append(f"Line {i} [{comment_type}]: {comment_text}")

    if not comments:
        return "No TODO/FIXME comments found"

    return "Comments found:\n" + "\n".join(comments)


@tool
def check_code_complexity(code: str) -> str:
    """
    Provide a basic complexity analysis of Python code.

    Args:
        code: Python code to analyze

    Returns:
        Complexity metrics
    """
    try:
        tree = ast.parse(code)

        total_lines = len(code.split("\n"))
        functions = [node for node in ast.walk(tree) if isinstance(node, ast.FunctionDef)]
        classes = [node for node in ast.walk(tree) if isinstance(node, ast.ClassDef)]
        conditionals = [node for node in ast.walk(tree) if isinstance(node, (ast.If, ast.While, ast.For))]
        try_blocks = [node for node in ast.walk(tree) if isinstance(node, ast.Try)]

        complexity_score = len(conditionals) + len(try_blocks) * 2

        analysis = [
            f"Code Complexity Analysis:",
            f"  Total lines: {total_lines}",
            f"  Functions: {len(functions)}",
            f"  Classes: {len(classes)}",
            f"  Conditionals (if/while/for): {len(conditionals)}",
            f"  Try-except blocks: {len(try_blocks)}",
            f"  Complexity score: {complexity_score}",
        ]

        if complexity_score < 5:
            analysis.append("  ✅ Low complexity - easy to maintain")
        elif complexity_score < 15:
            analysis.append("  ⚠️  Medium complexity - moderately complex")
        else:
            analysis.append("  ❌ High complexity - consider refactoring")

        return "\n".join(analysis)
    except Exception as e:
        return f"Error analyzing complexity: {str(e)}"


@tool
def validate_code_style(code: str) -> str:
    """
    Basic code style validation (naming conventions, line length).

    Args:
        code: Python code to validate

    Returns:
        Style issues found
    """
    issues = []

    lines = code.split("\n")

    # Check line length
    long_lines = [(i + 1, line) for i, line in enumerate(lines) if len(line) > 120]
    if long_lines:
        issues.append(f"⚠️  {len(long_lines)} line(s) exceed 120 characters")

    # Check for camelCase function names (Python prefers snake_case)
    camel_case_pattern = r"def [a-z]+[A-Z]"
    if re.search(camel_case_pattern, code):
        issues.append("⚠️  Found camelCase function names (prefer snake_case in Python)")

    # Check for missing docstrings in functions
    try:
        tree = ast.parse(code)
        functions = [node for node in ast.walk(tree) if isinstance(node, ast.FunctionDef)]
        functions_without_docstrings = [
            f.name for f in functions if not ast.get_docstring(f)
        ]
        if functions_without_docstrings:
            issues.append(
                f"⚠️  Functions without docstrings: {', '.join(functions_without_docstrings)}"
            )
    except:
        pass

    if not issues:
        return "✅ No major style issues found"

    return "Style Issues:\n" + "\n".join(issues)


# Export all tools
code_analysis_tools = [
    analyze_python_syntax,
    count_functions,
    check_imports,
    find_todos_in_code,
    check_code_complexity,
    validate_code_style
]
