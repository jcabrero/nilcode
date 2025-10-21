"""
Import validation and fixing tools for multi-language projects.
"""

import re
from typing import Dict, List, Set
from pathlib import Path
from langchain_core.tools import tool


@tool
def scan_all_imports(project_path: str = "./output") -> str:
    """
    Scan all files in the project and extract import statements.

    Args:
        project_path: Path to the project directory

    Returns:
        JSON string containing all imports by file
    """
    import json

    project = Path(project_path)
    if not project.exists():
        return json.dumps({"error": f"Project path {project_path} does not exist"})

    imports_by_file = {}

    # Scan Python files
    for py_file in project.rglob("*.py"):
        if "__pycache__" in str(py_file):
            continue

        try:
            content = py_file.read_text()
            python_imports = extract_python_imports(content)
            if python_imports:
                imports_by_file[str(py_file.relative_to(project))] = {
                    "language": "python",
                    "imports": python_imports
                }
        except Exception as e:
            imports_by_file[str(py_file.relative_to(project))] = {
                "error": str(e)
            }

    # Scan JavaScript/TypeScript files
    for js_file in project.rglob("*.[jt]s"):
        try:
            content = js_file.read_text()
            js_imports = extract_js_imports(content)
            if js_imports:
                imports_by_file[str(js_file.relative_to(project))] = {
                    "language": "javascript",
                    "imports": js_imports
                }
        except Exception as e:
            imports_by_file[str(js_file.relative_to(project))] = {
                "error": str(e)
            }

    # Also scan jsx/tsx
    for jsx_file in project.rglob("*.[jt]sx"):
        try:
            content = jsx_file.read_text()
            js_imports = extract_js_imports(content)
            if js_imports:
                imports_by_file[str(jsx_file.relative_to(project))] = {
                    "language": "javascript",
                    "imports": js_imports
                }
        except Exception as e:
            imports_by_file[str(jsx_file.relative_to(project))] = {
                "error": str(e)
            }

    return json.dumps(imports_by_file, indent=2)


def extract_python_imports(code: str) -> List[str]:
    """Extract import statements from Python code."""
    imports = []

    # Match "import x" or "import x as y"
    import_pattern = r'^import\s+([a-zA-Z0-9_., ]+?)(?:\s+as\s+[a-zA-Z0-9_]+)?$'
    # Match "from x import y" or "from x import (a, b, c)"
    from_pattern = r'^from\s+([a-zA-Z0-9_.]+)\s+import\s+(.+)$'

    for line in code.split('\n'):
        line = line.strip()

        # Skip comments
        if line.startswith('#'):
            continue

        # Check for import statement
        import_match = re.match(import_pattern, line, re.MULTILINE)
        if import_match:
            imports.append(line)
            continue

        # Check for from...import statement
        from_match = re.match(from_pattern, line, re.MULTILINE)
        if from_match:
            imports.append(line)

    return imports


def extract_js_imports(code: str) -> List[str]:
    """Extract import statements from JavaScript/TypeScript code."""
    imports = []

    # Match various import styles:
    # import X from 'module'
    # import { X, Y } from 'module'
    # import * as X from 'module'
    # const X = require('module')

    import_patterns = [
        r'import\s+.+?\s+from\s+["\'](.+?)["\']',
        r'import\s+["\'](.+?)["\']',
        r'const\s+.+?\s*=\s*require\(["\'](.+?)["\']\)',
        r'require\(["\'](.+?)["\']\)',
    ]

    for line in code.split('\n'):
        line = line.strip()

        # Skip comments
        if line.startswith('//') or line.startswith('/*'):
            continue

        for pattern in import_patterns:
            if re.search(pattern, line):
                imports.append(line.split('//')[0].strip())  # Remove inline comments
                break

    return imports


@tool
def validate_import_consistency(project_path: str = "./output") -> str:
    """
    Validate that imports are consistent across the project.
    Checks for:
    - Non-existent file imports
    - Mismatched module names
    - Missing exports

    Args:
        project_path: Path to the project directory

    Returns:
        Report of import issues found
    """
    import json

    project = Path(project_path)
    if not project.exists():
        return f"❌ Project path {project_path} does not exist"

    issues = []

    # Get all Python files
    py_files = {f.stem: f for f in project.rglob("*.py") if "__pycache__" not in str(f)}

    # Check Python imports
    for py_file in project.rglob("*.py"):
        if "__pycache__" in str(py_file):
            continue

        try:
            content = py_file.read_text()
            imports = extract_python_imports(content)

            for imp in imports:
                # Check "from X import Y" statements
                from_match = re.match(r'from\s+([a-zA-Z0-9_.]+)\s+import', imp)
                if from_match:
                    module = from_match.group(1)

                    # Check if it's a relative import
                    if module.startswith('.'):
                        # Relative import - check if file exists
                        rel_path = module.replace('.', '/')
                        expected_file = py_file.parent / f"{rel_path}.py"
                        if not expected_file.exists():
                            issues.append({
                                "file": str(py_file.relative_to(project)),
                                "line": imp,
                                "issue": f"Relative import '{module}' not found at {expected_file}",
                                "type": "missing_module"
                            })
                    elif not module.startswith('langchain') and not module.startswith('typing'):
                        # Local import - check if module exists
                        module_parts = module.split('.')
                        if module_parts[0] not in ['os', 'sys', 'json', 're', 'pathlib', 'datetime']:
                            # Could be a local module
                            if module_parts[0] not in py_files:
                                issues.append({
                                    "file": str(py_file.relative_to(project)),
                                    "line": imp,
                                    "issue": f"Module '{module_parts[0]}' not found in project",
                                    "type": "missing_module",
                                    "suggestion": f"Create {module_parts[0]}.py or install package"
                                })
        except Exception as e:
            issues.append({
                "file": str(py_file.relative_to(project)),
                "issue": f"Error reading file: {e}",
                "type": "read_error"
            })

    # Check JavaScript/TypeScript imports
    for js_file in list(project.rglob("*.[jt]s")) + list(project.rglob("*.[jt]sx")):
        try:
            content = js_file.read_text()
            imports = extract_js_imports(content)

            for imp in imports:
                # Extract module path
                match = re.search(r'["\'](.+?)["\']', imp)
                if match:
                    module_path = match.group(1)

                    # Check relative imports
                    if module_path.startswith('.'):
                        # Resolve relative path
                        expected_file = (js_file.parent / module_path).resolve()

                        # Check various extensions
                        found = False
                        for ext in ['', '.js', '.jsx', '.ts', '.tsx', '.json']:
                            if (Path(str(expected_file) + ext)).exists():
                                found = True
                                break

                        if not found:
                            issues.append({
                                "file": str(js_file.relative_to(project)),
                                "line": imp,
                                "issue": f"Relative import '{module_path}' not found",
                                "type": "missing_module"
                            })
        except Exception as e:
            issues.append({
                "file": str(js_file.relative_to(project)),
                "issue": f"Error reading file: {e}",
                "type": "read_error"
            })

    if not issues:
        return "✅ All imports are valid and consistent!"

    # Format report
    report = f"⚠️ Found {len(issues)} import issues:\n\n"
    for issue in issues:
        report += f"📁 {issue['file']}\n"
        if 'line' in issue:
            report += f"   Line: {issue['line']}\n"
        report += f"   Issue: {issue['issue']}\n"
        if 'suggestion' in issue:
            report += f"   💡 Suggestion: {issue['suggestion']}\n"
        report += "\n"

    return report


@tool
def suggest_import_fixes(file_path: str, project_path: str = "./output") -> str:
    """
    Suggest fixes for import issues in a specific file.

    Args:
        file_path: Path to the file to check (relative to project_path)
        project_path: Path to the project directory

    Returns:
        Suggested import fixes
    """
    project = Path(project_path)
    full_path = project / file_path

    if not full_path.exists():
        return f"❌ File {file_path} not found"

    try:
        content = full_path.read_text()
    except Exception as e:
        return f"❌ Error reading file: {e}"

    suggestions = []

    # Determine language
    if file_path.endswith('.py'):
        imports = extract_python_imports(content)

        for imp in imports:
            # Check for common issues
            if 'from typing import' in imp and 'Dict' in imp and 'List' not in imp:
                if 'List' in content:
                    suggestions.append({
                        "original": imp,
                        "suggested": imp.replace('import', 'import List,').replace(',,', ','),
                        "reason": "File uses List but doesn't import it"
                    })

    elif file_path.endswith(('.js', '.jsx', '.ts', '.tsx')):
        imports = extract_js_imports(content)

        # Check for React usage without import
        if ('</>' in content or '<div' in content or 'jsx' in content.lower()) and not any('react' in imp.lower() for imp in imports):
            suggestions.append({
                "original": None,
                "suggested": "import React from 'react'",
                "reason": "JSX detected but React not imported"
            })

    if not suggestions:
        return "✅ No import fixes suggested"

    report = f"💡 Suggested import fixes for {file_path}:\n\n"
    for sug in suggestions:
        if sug['original']:
            report += f"Replace:\n  {sug['original']}\nWith:\n  {sug['suggested']}\n"
        else:
            report += f"Add:\n  {sug['suggested']}\n"
        report += f"Reason: {sug['reason']}\n\n"

    return report


# Export all tools
import_validation_tools = [
    scan_all_imports,
    validate_import_consistency,
    suggest_import_fixes
]
