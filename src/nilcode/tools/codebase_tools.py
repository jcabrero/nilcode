"""
Codebase understanding and semantic search tools.
These tools help agents understand existing codebases and find relevant code.
"""

import os
import re
import ast
from pathlib import Path
from typing import List, Dict, Any, Optional
from langchain.tools import tool


@tool
def find_definition(symbol_name: str, search_path: str = ".") -> str:
    """
    Find the definition of a function, class, or variable in the codebase.
    
    Args:
        symbol_name: Name of the symbol to find (e.g., "MyClass", "my_function")
        search_path: Directory to search in (default: current directory)
    
    Returns:
        Location and definition of the symbol
    """
    try:
        search_dir = Path(search_path)
        if not search_dir.exists():
            return f"Error: Directory {search_path} does not exist"
        
        matches = []
        
        # Search Python files
        for py_file in search_dir.rglob("*.py"):
            try:
                with open(py_file, 'r', encoding='utf-8') as f:
                    content = f.read()
                    tree = ast.parse(content)
                    
                    for node in ast.walk(tree):
                        if isinstance(node, (ast.FunctionDef, ast.ClassDef, ast.AsyncFunctionDef)):
                            if node.name == symbol_name:
                                line_num = node.lineno
                                # Get a few lines of context
                                lines = content.split('\n')
                                start = max(0, line_num - 1)
                                end = min(len(lines), line_num + 5)
                                context = '\n'.join(lines[start:end])
                                
                                matches.append({
                                    'file': str(py_file.relative_to(search_dir)),
                                    'line': line_num,
                                    'type': type(node).__name__.replace('Def', ''),
                                    'context': context
                                })
            except:
                continue
        
        # Search JS/TS files for functions and classes
        for ext in ['*.js', '*.ts', '*.jsx', '*.tsx']:
            for js_file in search_dir.rglob(ext):
                try:
                    with open(js_file, 'r', encoding='utf-8') as f:
                        content = f.read()
                        lines = content.split('\n')
                        
                        for i, line in enumerate(lines):
                            # Match function/class definitions
                            patterns = [
                                rf'function\s+{symbol_name}\s*\(',
                                rf'const\s+{symbol_name}\s*=',
                                rf'let\s+{symbol_name}\s*=',
                                rf'class\s+{symbol_name}\s*',
                                rf'{symbol_name}\s*:\s*function',
                            ]
                            
                            if any(re.search(pattern, line) for pattern in patterns):
                                start = max(0, i)
                                end = min(len(lines), i + 6)
                                context = '\n'.join(lines[start:end])
                                
                                matches.append({
                                    'file': str(js_file.relative_to(search_dir)),
                                    'line': i + 1,
                                    'type': 'function/class',
                                    'context': context
                                })
                                break
                except:
                    continue
        
        if not matches:
            return f"No definition found for '{symbol_name}'"
        
        result = [f"Found {len(matches)} definition(s) for '{symbol_name}':\n"]
        for match in matches:
            result.append(f"\n📁 {match['file']}:{match['line']} ({match['type']})")
            result.append(f"```\n{match['context']}\n```")
        
        return '\n'.join(result)
    
    except Exception as e:
        return f"Error searching for definition: {str(e)}"


@tool
def find_usages(symbol_name: str, search_path: str = ".") -> str:
    """
    Find all usages of a function, class, or variable in the codebase.
    
    Args:
        symbol_name: Name of the symbol to find usages of
        search_path: Directory to search in
    
    Returns:
        List of files and lines where the symbol is used
    """
    try:
        search_dir = Path(search_path)
        if not search_dir.exists():
            return f"Error: Directory {search_path} does not exist"
        
        usages = []
        
        # Search all code files
        extensions = ['.py', '.js', '.ts', '.jsx', '.tsx', '.java', '.go', '.rs']
        for ext in extensions:
            for file_path in search_dir.rglob(f"*{ext}"):
                try:
                    with open(file_path, 'r', encoding='utf-8') as f:
                        lines = f.readlines()
                        
                    for i, line in enumerate(lines, 1):
                        if symbol_name in line and not line.strip().startswith('#'):
                            usages.append({
                                'file': str(file_path.relative_to(search_dir)),
                                'line': i,
                                'content': line.strip()
                            })
                except:
                    continue
        
        if not usages:
            return f"No usages found for '{symbol_name}'"
        
        # Group by file
        by_file = {}
        for usage in usages:
            if usage['file'] not in by_file:
                by_file[usage['file']] = []
            by_file[usage['file']].append(usage)
        
        result = [f"Found {len(usages)} usage(s) of '{symbol_name}' in {len(by_file)} file(s):\n"]
        for file_path, file_usages in list(by_file.items())[:20]:  # Limit to 20 files
            result.append(f"\n📁 {file_path}:")
            for usage in file_usages[:5]:  # Limit to 5 usages per file
                result.append(f"  Line {usage['line']}: {usage['content']}")
            if len(file_usages) > 5:
                result.append(f"  ... and {len(file_usages) - 5} more usages")
        
        if len(by_file) > 20:
            result.append(f"\n... and {len(by_file) - 20} more files")
        
        return '\n'.join(result)
    
    except Exception as e:
        return f"Error finding usages: {str(e)}"


@tool
def analyze_project_structure(search_path: str = ".") -> str:
    """
    Analyze the structure of a project to understand its organization.
    
    Args:
        search_path: Root directory to analyze
    
    Returns:
        Project structure summary with file counts, tech stack, and organization
    """
    try:
        root = Path(search_path)
        if not root.exists():
            return f"Error: Directory {search_path} does not exist"
        
        # Count files by type
        file_counts = {}
        directories = set()
        total_lines = 0
        
        code_extensions = {
            '.py': 'Python',
            '.js': 'JavaScript',
            '.ts': 'TypeScript',
            '.jsx': 'React (JSX)',
            '.tsx': 'React (TSX)',
            '.java': 'Java',
            '.go': 'Go',
            '.rs': 'Rust',
            '.html': 'HTML',
            '.css': 'CSS',
            '.json': 'JSON',
            '.yaml': 'YAML',
            '.yml': 'YAML',
            '.md': 'Markdown',
        }
        
        for file_path in root.rglob("*"):
            if file_path.is_file():
                # Skip common directories to ignore
                parts = file_path.relative_to(root).parts
                if any(skip in parts for skip in ['node_modules', '.git', '__pycache__', 'venv', '.venv', 'dist', 'build']):
                    continue
                
                ext = file_path.suffix
                if ext in code_extensions:
                    lang = code_extensions[ext]
                    file_counts[lang] = file_counts.get(lang, 0) + 1
                    
                    # Count lines for code files
                    try:
                        with open(file_path, 'r', encoding='utf-8') as f:
                            total_lines += len(f.readlines())
                    except:
                        pass
                
                # Track directories
                if file_path.parent != root:
                    directories.add(str(file_path.parent.relative_to(root).parts[0]))
        
        # Detect frameworks and tools
        frameworks = []
        config_files = {}
        
        for config_file in ['package.json', 'requirements.txt', 'pyproject.toml', 'go.mod', 'Cargo.toml', 'pom.xml']:
            config_path = root / config_file
            if config_path.exists():
                config_files[config_file] = True
                
                # Detect specific frameworks
                try:
                    with open(config_path, 'r', encoding='utf-8') as f:
                        content = f.read().lower()
                        if 'react' in content:
                            frameworks.append('React')
                        if 'vue' in content:
                            frameworks.append('Vue')
                        if 'fastapi' in content:
                            frameworks.append('FastAPI')
                        if 'django' in content:
                            frameworks.append('Django')
                        if 'flask' in content:
                            frameworks.append('Flask')
                        if 'express' in content:
                            frameworks.append('Express')
                except:
                    pass
        
        # Build summary
        result = ["Project Structure Analysis", "=" * 50, ""]
        
        result.append("📊 File Statistics:")
        for lang, count in sorted(file_counts.items(), key=lambda x: x[1], reverse=True):
            result.append(f"  • {lang}: {count} files")
        result.append(f"  • Total code lines: ~{total_lines:,}")
        result.append("")
        
        result.append("📁 Main Directories:")
        for dir_name in sorted(directories)[:10]:
            result.append(f"  • {dir_name}/")
        result.append("")
        
        if config_files:
            result.append("⚙️  Configuration Files:")
            for config in config_files:
                result.append(f"  • {config}")
            result.append("")
        
        if frameworks:
            result.append("🛠️  Detected Frameworks:")
            for framework in frameworks:
                result.append(f"  • {framework}")
            result.append("")
        
        # Tech stack summary
        result.append("💡 Tech Stack Summary:")
        languages = list(file_counts.keys())
        if languages:
            result.append(f"  Primary Languages: {', '.join(languages[:3])}")
        if frameworks:
            result.append(f"  Frameworks: {', '.join(frameworks)}")
        
        return '\n'.join(result)
    
    except Exception as e:
        return f"Error analyzing project: {str(e)}"


@tool
def list_files_recursively(directory: str = ".", pattern: str = "*.py", max_depth: int = 5) -> str:
    """
    List all files matching a pattern recursively.
    
    Args:
        directory: Directory to search in
        pattern: File pattern to match (e.g., "*.py", "*.js")
        max_depth: Maximum directory depth to search
    
    Returns:
        List of matching files with their relative paths
    """
    try:
        root = Path(directory)
        if not root.exists():
            return f"Error: Directory {directory} does not exist"
        
        files = []
        for file_path in root.rglob(pattern):
            # Skip common ignore directories
            parts = file_path.relative_to(root).parts
            if any(skip in parts for skip in ['node_modules', '.git', '__pycache__', 'venv', '.venv', 'dist', 'build']):
                continue
            
            # Check depth
            if len(parts) > max_depth:
                continue
            
            files.append(str(file_path.relative_to(root)))
        
        if not files:
            return f"No files matching '{pattern}' found in {directory}"
        
        # Sort and format
        files.sort()
        result = [f"Found {len(files)} file(s) matching '{pattern}':\n"]
        
        # Group by directory
        by_dir = {}
        for file_path in files:
            dir_name = str(Path(file_path).parent)
            if dir_name not in by_dir:
                by_dir[dir_name] = []
            by_dir[dir_name].append(Path(file_path).name)
        
        for dir_name, file_list in sorted(by_dir.items()):
            if dir_name == '.':
                result.append("📁 Root:")
            else:
                result.append(f"📁 {dir_name}/:")
            for filename in file_list[:20]:  # Limit files per directory
                result.append(f"  • {filename}")
            if len(file_list) > 20:
                result.append(f"  ... and {len(file_list) - 20} more files")
        
        return '\n'.join(result)
    
    except Exception as e:
        return f"Error listing files: {str(e)}"


@tool
def search_code_content(query: str, search_path: str = ".", file_pattern: str = "*.*") -> str:
    """
    Search for code content across files using regex or plain text.
    
    Args:
        query: Search query (supports regex)
        search_path: Directory to search in
        file_pattern: File pattern to search (e.g., "*.py", "*")
    
    Returns:
        Matching lines with file locations and context
    """
    try:
        root = Path(search_path)
        if not root.exists():
            return f"Error: Directory {search_path} does not exist"
        
        matches = []
        
        # Compile regex if it looks like a pattern
        try:
            pattern = re.compile(query, re.IGNORECASE)
            is_regex = True
        except:
            pattern = query.lower()
            is_regex = False
        
        # Search files
        for file_path in root.rglob(file_pattern):
            if not file_path.is_file():
                continue
            
            # Skip binary and ignored files
            parts = file_path.relative_to(root).parts
            if any(skip in parts for skip in ['node_modules', '.git', '__pycache__', 'venv', '.venv', 'dist', 'build']):
                continue
            
            # Skip binary files
            if file_path.suffix in ['.pyc', '.so', '.dll', '.exe', '.bin']:
                continue
            
            try:
                with open(file_path, 'r', encoding='utf-8') as f:
                    lines = f.readlines()
                
                for i, line in enumerate(lines, 1):
                    match = False
                    if is_regex:
                        match = pattern.search(line)
                    else:
                        match = pattern in line.lower()
                    
                    if match:
                        # Get context lines
                        context_start = max(0, i - 2)
                        context_end = min(len(lines), i + 1)
                        context = ''.join(lines[context_start:context_end])
                        
                        matches.append({
                            'file': str(file_path.relative_to(root)),
                            'line': i,
                            'content': line.strip(),
                            'context': context
                        })
            except:
                continue
        
        if not matches:
            return f"No matches found for query: '{query}'"
        
        # Limit results
        matches = matches[:50]
        
        result = [f"Found {len(matches)} match(es) for '{query}':\n"]
        
        current_file = None
        for match in matches[:30]:  # Show first 30 matches
            if match['file'] != current_file:
                result.append(f"\n📁 {match['file']}:")
                current_file = match['file']
            result.append(f"  Line {match['line']}: {match['content'][:100]}")
        
        if len(matches) > 30:
            result.append(f"\n... and {len(matches) - 30} more matches")
        
        return '\n'.join(result)
    
    except Exception as e:
        return f"Error searching code: {str(e)}"


# Export all tools
codebase_tools = [
    find_definition,
    find_usages,
    analyze_project_structure,
    list_files_recursively,
    search_code_content,
]

