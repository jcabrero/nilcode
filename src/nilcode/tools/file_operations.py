"""
File operation tools for reading, writing, and editing files.
These tools will be used by the developer agents.
"""

import os
from pathlib import Path
from typing import Optional
from langchain.tools import tool


@tool
def read_file(file_path: str) -> str:
    """
    Read the contents of a file.

    Args:
        file_path: Path to the file to read

    Returns:
        Contents of the file as a string
    """
    try:
        path = Path(file_path)
        if not path.exists():
            return f"Error: File {file_path} does not exist"

        with open(path, 'r', encoding='utf-8') as f:
            content = f.read()

        return f"File: {file_path}\n\n{content}"
    except Exception as e:
        return f"Error reading file {file_path}: {str(e)}"


@tool
def write_file(file_path: str, content: str) -> str:
    """
    Write content to a file. Creates the file if it doesn't exist.
    Creates parent directories if needed.

    Args:
        file_path: Path to the file to write
        content: Content to write to the file

    Returns:
        Success or error message
    """
    try:
        path = Path(file_path)

        # Create parent directories if they don't exist
        path.parent.mkdir(parents=True, exist_ok=True)

        with open(path, 'w', encoding='utf-8') as f:
            f.write(content)

        return f"Successfully wrote to {file_path}"
    except Exception as e:
        return f"Error writing to file {file_path}: {str(e)}"


@tool
def edit_file(file_path: str, old_string: str, new_string: str) -> str:
    """
    Edit a file by replacing old_string with new_string.

    Args:
        file_path: Path to the file to edit
        old_string: String to find and replace
        new_string: String to replace with

    Returns:
        Success or error message
    """
    try:
        path = Path(file_path)
        if not path.exists():
            return f"Error: File {file_path} does not exist"

        with open(path, 'r', encoding='utf-8') as f:
            content = f.read()

        if old_string not in content:
            return f"Error: String not found in {file_path}"

        # Check if replacement would be unique
        occurrences = content.count(old_string)
        if occurrences > 1:
            return f"Error: String appears {occurrences} times in {file_path}. Please provide a more specific string."

        new_content = content.replace(old_string, new_string)

        with open(path, 'w', encoding='utf-8') as f:
            f.write(new_content)

        return f"Successfully edited {file_path}"
    except Exception as e:
        return f"Error editing file {file_path}: {str(e)}"


@tool
def list_files(directory: str, pattern: str = "*") -> str:
    """
    List files in a directory matching a pattern.

    Args:
        directory: Directory to search in
        pattern: Glob pattern to match files (default: "*")

    Returns:
        List of matching files
    """
    try:
        path = Path(directory)
        if not path.exists():
            return f"Error: Directory {directory} does not exist"

        if not path.is_dir():
            return f"Error: {directory} is not a directory"

        files = list(path.glob(pattern))
        if not files:
            return f"No files matching pattern '{pattern}' in {directory}"

        file_list = "\n".join([str(f.relative_to(path)) for f in files if f.is_file()])
        return f"Files in {directory}:\n{file_list}"
    except Exception as e:
        return f"Error listing files in {directory}: {str(e)}"


@tool
def create_directory(directory_path: str) -> str:
    """
    Create a directory and any necessary parent directories.

    Args:
        directory_path: Path to the directory to create

    Returns:
        Success or error message
    """
    try:
        path = Path(directory_path)
        path.mkdir(parents=True, exist_ok=True)
        return f"Successfully created directory {directory_path}"
    except Exception as e:
        return f"Error creating directory {directory_path}: {str(e)}"


# Export all tools
file_tools = [
    read_file,
    write_file,
    edit_file,
    list_files,
    create_directory
]
