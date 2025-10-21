# Version System Documentation

## Overview

NilCode now includes a comprehensive version management system that helps you identify which version you're using and track changes across releases.

## Current Version

**Version 2.0.0 "Validator"**
Released: 2025-01-21

## Displaying Version Information

### Method 1: Command Line Flag

```bash
# Show detailed version information
uv run nilcode --version
uv run nilcode -v

# Show changelog
uv run nilcode --changelog
```

### Method 2: Interactive Mode

```bash
# Start interactive mode
uv run nilcode

# Then type these commands:
version     # Show version information
changelog   # Show version changelog
```

### Method 3: Python API

```python
from nilcode.version import (
    get_version,
    get_version_info,
    print_banner,
    print_version_info,
    print_changelog
)

# Get version string
version = get_version()  # Returns "2.0.0"

# Get detailed info
info = get_version_info()
print(info)
# {
#     "version": "2.0.0",
#     "name": "Validator",
#     "release_date": "2025-01-21",
#     "history": {...}
# }

# Print banner with version
print_banner()

# Print detailed version info
print_version_info()

# Print changelog
print_changelog(limit=3)  # Show last 3 versions
```

## Version Banner

When you start NilCode, you'll see this banner:

```
╔══════════════════════════════════════════════════════════════════╗
║                                                                  ║
║   ███╗   ██╗██╗██╗      ██████╗ ██████╗ ██████╗ ███████╗       ║
║   ████╗  ██║██║██║     ██╔════╝██╔═══██╗██╔══██╗██╔════╝       ║
║   ██╔██╗ ██║██║██║     ██║     ██║   ██║██║  ██║█████╗         ║
║   ██║╚██╗██║██║██║     ██║     ██║   ██║██║  ██║██╔══╝         ║
║   ██║ ╚████║██║███████╗╚██████╗╚██████╔╝██████╔╝███████╗       ║
║   ╚═╝  ╚═══╝╚═╝╚══════╝ ╚═════╝ ╚═════╝ ╚═════╝ ╚══════╝       ║
║                                                                  ║
║              Multi-Agent AI Development System                   ║
║                                                                  ║
║  Version: 2.0.0 "Validator"                                     ║
║  Released: 2025-01-21                                           ║
║                                                                  ║
║  Features:                                                       ║
║  ✓ Syntax Validation & Error Correction                         ║
║  ✓ Language-Agnostic Code Generation                            ║
║  ✓ Architectural Consistency Enforcement                        ║
║  ✓ Multi-Stage Quality Assurance                                ║
║                                                                  ║
║  Supported Languages: Python, JavaScript, TypeScript, HTML      ║
║  Frameworks: React, Vue, FastAPI, Flask, Django, Express        ║
║                                                                  ║
╚══════════════════════════════════════════════════════════════════╝
```

## Version Naming Convention

NilCode uses **Semantic Versioning** with code names:

- **Major.Minor.Patch** (e.g., 2.0.0)
- **Code Name** (e.g., "Validator")

### Version Components

- **Major**: Significant changes, may include breaking changes
- **Minor**: New features, backward compatible
- **Patch**: Bug fixes, backward compatible

### Code Names

Each major version has a meaningful code name:
- **v1.0 "Genesis"**: Initial release
- **v2.0 "Validator"**: Syntax validation and quality assurance

## Version History

### v2.0.0 "Validator" (2025-01-21)

**Major Features:**
- ✓ Comprehensive syntax validation
- ✓ Project manifest system
- ✓ Language/framework auto-detection
- ✓ Enhanced agent coordination
- ✓ Multi-stage validation
- ✓ Robust error handling

**Key Improvements:**
- Eliminates syntax errors through mandatory validation
- Ensures architectural consistency via shared manifests
- Supports any programming language
- Self-corrects errors automatically

### v1.0.0 "Genesis" (2025-01-15)

**Initial Release:**
- Multi-agent workflow system
- Basic file operations
- Python code analysis
- Interactive CLI

## Checking Version Compatibility

```python
from nilcode.version import check_version_compatibility

# Check if current version meets requirement
if check_version_compatibility("2.0.0"):
    print("Version compatible!")
else:
    print("Please upgrade to version 2.0.0 or higher")
```

## Files Containing Version Information

1. **`src/nilcode/version.py`**: Main version module
   - Version constants
   - Version history
   - Banner generation
   - Utility functions

2. **`pyproject.toml`**: Package version
   - Used by build tools
   - Should match version.py

3. **`CHANGELOG.md`**: Detailed change log
   - All changes documented
   - Migration guides
   - Breaking changes noted

## Updating Versions (For Developers)

When releasing a new version:

1. Update `src/nilcode/version.py`:
   ```python
   __version__ = "2.1.0"
   __version_name__ = "NewName"
   __release_date__ = "2025-02-01"
   ```

2. Add to `VERSION_HISTORY` in `version.py`:
   ```python
   "2.1.0": {
       "name": "NewName",
       "date": "2025-02-01",
       "description": "...",
       "features": [...],
       "breaking_changes": [...]
   }
   ```

3. Update `pyproject.toml`:
   ```toml
   version = "2.1.0"
   ```

4. Add entry to `CHANGELOG.md`:
   ```markdown
   ## [2.1.0] - 2025-02-01 "NewName"
   ...
   ```

5. Test version display:
   ```bash
   uv run nilcode --version
   ```

## Version Queries

### CLI Commands

```bash
# Show version
uv run nilcode --version
uv run nilcode -v
uv run nilcode version

# Show changelog
uv run nilcode --changelog
uv run nilcode changelog
```

### Interactive Commands

```
What would you like to build?
> version

What would you like to build?
> changelog
```

### Direct Python Import

```python
import nilcode.version as nv

print(f"Running NilCode {nv.get_version()}")
```

## Benefits of Version System

1. **Clear Identification**: Always know which version you're running
2. **Feature Tracking**: Understand what features are available
3. **Change Awareness**: Stay informed about improvements
4. **Compatibility**: Check version requirements
5. **Debugging**: Report issues with specific version info

## Quick Reference

| Command | Description |
|---------|-------------|
| `uv run nilcode --version` | Show version info |
| `uv run nilcode -v` | Show version info (short) |
| `uv run nilcode --changelog` | Show full changelog |
| `version` (in CLI) | Show version info |
| `changelog` (in CLI) | Show changelog |

## Example Session

```bash
$ uv run nilcode --version

======================================================================
NilCode Version 2.0.0 "Validator"
Released: 2025-01-21
======================================================================

Description:
  Major upgrade with syntax validation and language-agnostic design

Features:
  ✓ Comprehensive syntax validation for Python, JavaScript, HTML, JSON
  ✓ Project manifest system for architectural consistency
  ✓ Language/framework auto-detection
  ✓ Enhanced agent coordination with shared documentation
  ✓ Multi-stage validation with self-correction
  ✓ Robust error handling across all agents
```

## Troubleshooting

### Version Not Displaying

If version information doesn't display:

1. Check installation:
   ```bash
   uv sync
   ```

2. Verify version module:
   ```bash
   uv run python -c "from nilcode.version import get_version; print(get_version())"
   ```

3. Check pyproject.toml matches:
   ```bash
   grep version pyproject.toml
   ```

### Version Mismatch

If versions don't match:

1. Rebuild package:
   ```bash
   uv sync --reinstall-package nilcode
   ```

2. Clear cache:
   ```bash
   uv cache clean
   ```

## Related Documentation

- **CHANGELOG.md**: Detailed version history
- **IMPROVEMENTS.md**: Technical documentation
- **UPGRADE_SUMMARY.md**: Quick upgrade guide

## Support

For version-related issues:
1. Check you're running the latest version
2. Read the changelog for known issues
3. Report bugs with version information included
