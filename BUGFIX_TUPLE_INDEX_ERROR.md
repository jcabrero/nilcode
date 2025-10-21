# Bug Fix: Tuple Index Out of Range Error

## Problem
When running `nilcode` with a user request, the system crashed with:
```
IndexError: tuple index out of range
```

## Root Cause Analysis

The error was caused by **unescaped curly braces in prompt templates** that were being interpreted as Python format string placeholders.

### Detailed Trace
The full error occurred in the frontend_developer agent when it tried to format its prompt:
```python
messages = prompt.format_messages(
    user_request=state["user_request"],
    plan=state.get("plan", ""),
    frontend_tech=", ".join(state.get("frontend_tech", [])) or "Not specified",
    manifest_path=state.get("project_manifest_path", "PROJECT_MANIFEST.md"),
    guidelines_path=state.get("guidelines_path", ".agent-guidelines"),
    task_content=current_task["content"]
)
```

Python's string formatter interpreted bare `{}` in the prompt text as positional format placeholders, but since only keyword arguments were provided, it tried to access a tuple index that didn't exist.

## Files Fixed

### 1. `/src/nilcode/agents/frontend_developer.py`

**Lines 68-70 (FRONTEND_SYSTEM_PROMPT):**

❌ **Before:**
```python
SYNTAX REQUIREMENTS:
- JavaScript/TypeScript: Balanced braces {}, brackets [], parentheses ()
- Proper function declarations: function name() {} or const name = () => {}
- Valid import statements: import { X } from 'module' or import X from 'module'
```

✅ **After:**
```python
SYNTAX REQUIREMENTS:
- JavaScript/TypeScript: Balanced braces {{}}, brackets [], parentheses ()
- Proper function declarations: function name() {{}} or const name = () => {{}}
- Valid import statements: import {{ X }} from 'module' or import X from 'module'
```

### 2. `/src/nilcode/agents/backend_developer.py`

**Lines 80-81 (BACKEND_SYSTEM_PROMPT):**

❌ **Before:**
```python
SYNTAX REQUIREMENTS FOR JAVASCRIPT/NODE:
- Balanced braces {}, brackets [], parentheses ()
- Proper function declarations: function name() {} or const name = () => {}
```

✅ **After:**
```python
SYNTAX REQUIREMENTS FOR JAVASCRIPT/NODE:
- Balanced braces {{}}, brackets [], parentheses ()
- Proper function declarations: function name() {{}} or const name = () => {{}}
```

### 3. `/src/nilcode/cli.py` (Line 287)

**Additional defensive fix:**

✅ **Added check for empty state updates:**
```python
if state_update and len(state_update.keys()) > 0:
    agent_name = list(state_update.keys())[0]
```

### 4. `/src/nilcode/tools/codebase_tools.py` (Line 229-231)

**Additional defensive fix:**

✅ **Added check before accessing tuple index:**
```python
# Track directories
if file_path.parent != root:
    rel_path = file_path.parent.relative_to(root)
    if rel_path.parts:  # Only access [0] if parts exist
        directories.add(str(rel_path.parts[0]))
```

## Why This Happened

In Python format strings:
- `{}` = positional placeholder (expects args like `format(value1, value2)`)
- `{name}` = keyword placeholder (expects kwargs like `format(name=value)`)
- `{{}}` = escaped literal braces (renders as `{}`)

When documenting syntax that includes literal braces (like JavaScript function syntax), you must escape them as `{{}}` in format strings.

## Solution Summary

1. **Escaped all curly braces** in prompt templates where they represent literal syntax examples
2. **Added defensive checks** in CLI and tools to handle edge cases with empty collections
3. **Verified** no other agents have similar issues

## Testing

After these fixes:
- ✅ Prompt formatting works correctly
- ✅ CLI handles empty state updates gracefully
- ✅ Codebase analysis handles edge cases
- ✅ No linter errors introduced

## Prevention

When writing agent prompts that include syntax examples:
- **Always escape** literal braces: `{{}}` instead of `{}`
- **Test** prompt formatting with actual state data
- **Document** syntax examples carefully to avoid confusion

## Related Issues

This is similar to issues that occur when:
- Using f-strings with regex patterns containing `{}`
- Writing documentation strings with JSON/JavaScript examples
- Creating templates that need to show literal placeholder syntax

## Version

Fixed in: **NilCode v2.0.0 "Validator"**
Date: **2025-01-21**

