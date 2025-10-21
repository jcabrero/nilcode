"""
Validation tools for syntax checking and code quality validation.
These tools help agents validate their code before marking tasks complete.
"""

import ast
from pathlib import Path
from langchain.tools import tool


@tool
def validate_python_syntax(code: str) -> str:
    """
    Validate Python code syntax without executing it.

    Args:
        code: Python code string to validate

    Returns:
        Success message or detailed syntax error
    """
    try:
        ast.parse(code)
        return "✓ Python syntax is valid"
    except SyntaxError as e:
        return f"✗ Syntax Error at line {e.lineno}, column {e.offset}:\n{e.msg}\n{e.text}"
    except Exception as e:
        return f"✗ Validation error: {str(e)}"


@tool
def validate_python_file(file_path: str) -> str:
    """
    Validate syntax of a Python file.

    Args:
        file_path: Path to the Python file

    Returns:
        Success message or detailed syntax error
    """
    try:
        path = Path(file_path)
        if not path.exists():
            return f"✗ File {file_path} does not exist"

        if not file_path.endswith('.py'):
            return f"✗ File {file_path} is not a Python file"

        with open(path, 'r', encoding='utf-8') as f:
            code = f.read()

        return validate_python_syntax.invoke({"code": code})
    except Exception as e:
        return f"✗ Error reading file: {str(e)}"


@tool
def validate_javascript_syntax(code: str) -> str:
    """
    Perform basic JavaScript/TypeScript syntax validation.
    Checks for common syntax errors.

    Args:
        code: JavaScript/TypeScript code to validate

    Returns:
        Success message or list of potential issues
    """
    issues = []

    # Check for common syntax errors
    lines = code.split('\n')

    # Track bracket/brace balance
    open_braces = code.count('{')
    close_braces = code.count('}')
    open_brackets = code.count('[')
    close_brackets = code.count(']')
    open_parens = code.count('(')
    close_parens = code.count(')')

    if open_braces != close_braces:
        issues.append(f"✗ Unbalanced braces: {open_braces} open, {close_braces} close")
    if open_brackets != close_brackets:
        issues.append(f"✗ Unbalanced brackets: {open_brackets} open, {close_brackets} close")
    if open_parens != close_parens:
        issues.append(f"✗ Unbalanced parentheses: {open_parens} open, {close_parens} close")

    # Check for common typos
    for i, line in enumerate(lines, 1):
        # Function/arrow function syntax
        if 'fucntion' in line or 'funtion' in line:
            issues.append(f"✗ Line {i}: Possible typo in 'function' keyword")

        # Check for missing semicolons in obvious places (optional but helpful)
        stripped = line.strip()
        if stripped.endswith('return') or (stripped.startswith('var ') and '=' in stripped and not stripped.endswith(';')):
            issues.append(f"⚠ Line {i}: Possible missing semicolon")

    # Check for unterminated strings (basic check)
    in_string = False
    string_char = None
    for i, line in enumerate(lines, 1):
        for char in line:
            if char in ['"', "'", '`'] and (not string_char or string_char == char):
                if not in_string:
                    in_string = True
                    string_char = char
                else:
                    in_string = False
                    string_char = None

    if issues:
        return "JavaScript/TypeScript validation found issues:\n" + "\n".join(issues)

    return "✓ Basic JavaScript/TypeScript syntax checks passed"


@tool
def validate_json_syntax(json_string: str) -> str:
    """
    Validate JSON syntax.

    Args:
        json_string: JSON string to validate

    Returns:
        Success message or error details
    """
    import json
    try:
        json.loads(json_string)
        return "✓ JSON syntax is valid"
    except json.JSONDecodeError as e:
        return f"✗ JSON Syntax Error at line {e.lineno}, column {e.colno}:\n{e.msg}"
    except Exception as e:
        return f"✗ JSON validation error: {str(e)}"


@tool
def validate_html_syntax(html: str) -> str:
    """
    Perform basic HTML syntax validation.
    Checks for unclosed tags and basic structure.

    Args:
        html: HTML string to validate

    Returns:
        Success message or list of issues
    """
    issues = []

    # Basic tag matching (simplified)
    tag_pattern = r'<(\w+)[^>]*?>'
    close_tag_pattern = r'</(\w+)>'
    self_closing = {'img', 'br', 'hr', 'input', 'meta', 'link', 'area', 'base', 'col', 'embed', 'source', 'track', 'wbr'}

    open_tags = []

    # Find all tags
    import re
    for match in re.finditer(tag_pattern, html):
        tag = match.group(1).lower()
        if tag not in self_closing:
            # Check if it's self-closing with />
            full_tag = match.group(0)
            if not full_tag.endswith('/>'):
                open_tags.append(tag)

    # Find all closing tags
    for match in re.finditer(close_tag_pattern, html):
        tag = match.group(1).lower()
        if open_tags and open_tags[-1] == tag:
            open_tags.pop()
        else:
            issues.append(f"✗ Unexpected closing tag: </{tag}>")

    # Check for unclosed tags
    if open_tags:
        issues.append(f"✗ Unclosed tags: {', '.join(open_tags)}")

    if issues:
        return "HTML validation found issues:\n" + "\n".join(issues)

    return "✓ Basic HTML syntax checks passed"


@tool
def check_import_validity(file_path: str, language: str) -> str:
    """
    Check if imports/requires in a file are properly formatted.

    Args:
        file_path: Path to the file
        language: Programming language (python, javascript, typescript)

    Returns:
        Report of import validity
    """
    try:
        path = Path(file_path)
        if not path.exists():
            return f"✗ File {file_path} does not exist"

        with open(path, 'r', encoding='utf-8') as f:
            content = f.read()

        issues = []

        if language == "python":
            # Check for common Python import issues
            for i, line in enumerate(content.split('\n'), 1):
                stripped = line.strip()
                if stripped.startswith('import ') or stripped.startswith('from '):
                    # Check for syntax issues
                    if stripped.startswith('import') and not stripped.startswith('import '):
                        issues.append(f"Line {i}: Missing space after 'import'")
                    if stripped.startswith('from') and ' import ' not in stripped:
                        issues.append(f"Line {i}: Invalid 'from' import syntax")

        elif language in ["javascript", "typescript"]:
            # Check for JavaScript/TypeScript imports
            for i, line in enumerate(content.split('\n'), 1):
                stripped = line.strip()
                if stripped.startswith('import '):
                    # Basic check for import syntax
                    if ' from ' not in stripped and not stripped.endswith(';'):
                        issues.append(f"Line {i}: Possible incomplete import statement")

        if issues:
            return f"Import validation found {len(issues)} issue(s):\n" + "\n".join(issues)

        return f"✓ Import statements appear valid for {language}"

    except Exception as e:
        return f"✗ Error checking imports: {str(e)}"


@tool
def auto_detect_language(file_path: str) -> str:
    """
    Automatically detect the programming language of a file.

    Args:
        file_path: Path to the file

    Returns:
        Detected language or 'unknown'
    """
    extension_map = {
        '.py': 'python',
        '.js': 'javascript',
        '.jsx': 'javascript',
        '.ts': 'typescript',
        '.tsx': 'typescript',
        '.html': 'html',
        '.htm': 'html',
        '.css': 'css',
        '.json': 'json',
        '.java': 'java',
        '.cpp': 'cpp',
        '.c': 'c',
        '.go': 'go',
        '.rs': 'rust',
        '.rb': 'ruby',
        '.php': 'php',
    }

    path = Path(file_path)
    extension = path.suffix.lower()

    language = extension_map.get(extension, 'unknown')
    return f"Detected language: {language} (extension: {extension})"


# Export all validation tools
validation_tools = [
    validate_python_syntax,
    validate_python_file,
    validate_javascript_syntax,
    validate_json_syntax,
    validate_html_syntax,
    check_import_validity,
    auto_detect_language,
]
