"""
File verification tools for confirming files are actually created and tracking their status.
These tools help ensure files exist and contain expected content.
"""

import os
import time
from pathlib import Path
from typing import List, Dict, Any, Optional
from langchain.tools import tool


@tool
def verify_file_exists(file_path: str) -> str:
    """
    Verify that a file exists and return its status.
    
    Args:
        file_path: Path to the file to verify
        
    Returns:
        Status message with file details
    """
    try:
        path = Path(file_path)
        
        if not path.exists():
            return f"❌ File does not exist: {file_path}"
        
        if not path.is_file():
            return f"❌ Path exists but is not a file: {file_path}"
        
        # Get file stats
        stat = path.stat()
        size = stat.st_size
        modified_time = time.ctime(stat.st_mtime)
        
        return f"✅ File verified: {file_path} (size: {size} bytes, modified: {modified_time})"
        
    except Exception as e:
        return f"❌ Error verifying file {file_path}: {str(e)}"


@tool
def verify_file_content(file_path: str, expected_content: str = None, min_size: int = 0) -> str:
    """
    Verify file exists and optionally check its content.
    
    Args:
        file_path: Path to the file to verify
        expected_content: Optional content that should be in the file
        min_size: Minimum file size in bytes
        
    Returns:
        Verification result with content analysis
    """
    try:
        path = Path(file_path)
        
        if not path.exists():
            return f"❌ File does not exist: {file_path}"
        
        if not path.is_file():
            return f"❌ Path exists but is not a file: {file_path}"
        
        # Check file size
        size = path.stat().st_size
        if size < min_size:
            return f"❌ File too small: {file_path} (size: {size} bytes, minimum: {min_size})"
        
        # Read and analyze content
        with open(path, 'r', encoding='utf-8') as f:
            content = f.read()
        
        result = f"✅ File verified: {file_path} (size: {size} bytes)"
        
        # Check for expected content
        if expected_content:
            if expected_content in content:
                result += f" ✅ Contains expected content"
            else:
                result += f" ⚠️ Does not contain expected content"
        
        # Basic content analysis
        lines = content.split('\n')
        non_empty_lines = [line for line in lines if line.strip()]
        
        result += f"\n📊 Content analysis: {len(lines)} total lines, {len(non_empty_lines)} non-empty lines"
        
        # Check for common issues
        if content.strip() == "":
            result += f"\n⚠️ File is empty"
        elif len(non_empty_lines) < 3:
            result += f"\n⚠️ File has very few lines"
        
        return result
        
    except Exception as e:
        return f"❌ Error verifying file content {file_path}: {str(e)}"


@tool
def verify_multiple_files(file_paths: List[str]) -> str:
    """
    Verify multiple files exist and return a summary.
    
    Args:
        file_paths: List of file paths to verify
        
    Returns:
        Summary of file verification results
    """
    results = []
    existing_count = 0
    missing_count = 0
    
    for file_path in file_paths:
        try:
            path = Path(file_path)
            if path.exists() and path.is_file():
                size = path.stat().st_size
                results.append(f"✅ {file_path} ({size} bytes)")
                existing_count += 1
            else:
                results.append(f"❌ {file_path} (missing)")
                missing_count += 1
        except Exception as e:
            results.append(f"❌ {file_path} (error: {str(e)})")
            missing_count += 1
    
    summary = f"📊 File Verification Summary:\n"
    summary += f"✅ Existing: {existing_count}\n"
    summary += f"❌ Missing: {missing_count}\n"
    summary += f"📁 Total: {len(file_paths)}\n\n"
    summary += "\n".join(results)
    
    return summary


@tool
def check_file_permissions(file_path: str) -> str:
    """
    Check file permissions and accessibility.
    
    Args:
        file_path: Path to the file to check
        
    Returns:
        Permission status and details
    """
    try:
        path = Path(file_path)
        
        if not path.exists():
            return f"❌ File does not exist: {file_path}"
        
        # Check read permission
        readable = os.access(path, os.R_OK)
        writable = os.access(path, os.W_OK)
        executable = os.access(path, os.X_OK)
        
        result = f"📁 File permissions for {file_path}:\n"
        result += f"  Read: {'✅' if readable else '❌'}\n"
        result += f"  Write: {'✅' if writable else '❌'}\n"
        result += f"  Execute: {'✅' if executable else '❌'}\n"
        
        # Get file mode
        mode = oct(path.stat().st_mode)[-3:]
        result += f"  Mode: {mode}\n"
        
        return result
        
    except Exception as e:
        return f"❌ Error checking permissions for {file_path}: {str(e)}"


@tool
def verify_directory_structure(directory: str, expected_files: List[str] = None) -> str:
    """
    Verify a directory structure and optionally check for expected files.
    
    Args:
        directory: Directory path to verify
        expected_files: Optional list of files that should exist in the directory
        
    Returns:
        Directory structure verification result
    """
    try:
        path = Path(directory)
        
        if not path.exists():
            return f"❌ Directory does not exist: {directory}"
        
        if not path.is_dir():
            return f"❌ Path exists but is not a directory: {directory}"
        
        # List all files in directory
        all_files = []
        for item in path.rglob('*'):
            if item.is_file():
                rel_path = item.relative_to(path)
                all_files.append(str(rel_path))
        
        result = f"📁 Directory structure for {directory}:\n"
        result += f"  Total files: {len(all_files)}\n"
        
        if all_files:
            result += f"  Files found:\n"
            for file in sorted(all_files)[:20]:  # Show first 20 files
                result += f"    - {file}\n"
            if len(all_files) > 20:
                result += f"    ... and {len(all_files) - 20} more files\n"
        
        # Check for expected files
        if expected_files:
            result += f"\n🔍 Checking expected files:\n"
            found_expected = 0
            for expected_file in expected_files:
                if expected_file in all_files:
                    result += f"  ✅ {expected_file}\n"
                    found_expected += 1
                else:
                    result += f"  ❌ {expected_file} (missing)\n"
            
            result += f"\n📊 Expected files: {found_expected}/{len(expected_files)} found"
        
        return result
        
    except Exception as e:
        return f"❌ Error verifying directory {directory}: {str(e)}"


@tool
def get_file_checksum(file_path: str) -> str:
    """
    Get a simple checksum of a file for verification.
    
    Args:
        file_path: Path to the file
        
    Returns:
        File checksum and basic info
    """
    try:
        import hashlib
        
        path = Path(file_path)
        
        if not path.exists():
            return f"❌ File does not exist: {file_path}"
        
        if not path.is_file():
            return f"❌ Path exists but is not a file: {file_path}"
        
        # Calculate MD5 hash
        hash_md5 = hashlib.md5()
        with open(path, "rb") as f:
            for chunk in iter(lambda: f.read(4096), b""):
                hash_md5.update(chunk)
        
        checksum = hash_md5.hexdigest()
        size = path.stat().st_size
        
        return f"📄 File: {file_path}\nSize: {size} bytes\nMD5: {checksum}"
        
    except Exception as e:
        return f"❌ Error calculating checksum for {file_path}: {str(e)}"


# Export all tools
file_verification_tools = [
    verify_file_exists,
    verify_file_content,
    verify_multiple_files,
    check_file_permissions,
    verify_directory_structure,
    get_file_checksum
]
