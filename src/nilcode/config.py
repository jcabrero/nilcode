"""
Configuration management for NilCode projects.
Supports .nilcoderc and .nilcode.json configuration files.
"""

import json
import os
from pathlib import Path
from typing import Dict, Any, Optional, List


DEFAULT_CONFIG = {
    "project_name": "",
    "working_directory": ".",
    "ignore_patterns": [
        "node_modules/**",
        ".git/**",
        "__pycache__/**",
        "*.pyc",
        ".venv/**",
        "venv/**",
        "dist/**",
        "build/**",
        ".cache/**",
        "*.egg-info/**"
    ],
    "agent_settings": {
        "planner": {
            "temperature": 0.3,
            "max_tasks": 20
        },
        "software_architect": {
            "temperature": 0.2
        },
        "coder": {
            "temperature": 0.2,
            "preferred_frameworks": []
        },
        "tester": {
            "temperature": 0.1,
            "auto_run_tests": True
        },
        "error_recovery": {
            "temperature": 0.1,
            "max_iterations": 5,
            "auto_fix": True
        },
        "orchestrator": {
            "temperature": 0.2
        }
    },
    "llm_settings": {
        "model": "openai/gpt-oss-120b",
        "base_url": None,
        "max_tokens": 4096,
        "timeout": 60
    },
    "workflow_settings": {
        "enable_error_recovery": True,
        "enable_auto_testing": True,
        "enable_auto_linting": False,
        "max_workflow_iterations": 20
    },
    "file_settings": {
        "max_file_size": 1048576,  # 1MB
        "encoding": "utf-8",
        "line_ending": "lf"
    },
    "output_settings": {
        "verbose": True,
        "show_streaming": True,
        "show_tool_calls": True,
        "color_output": True
    }
}


class NilCodeConfig:
    """Configuration manager for NilCode projects."""

    def __init__(self, config_path: Optional[str] = None):
        """
        Initialize configuration.

        Args:
            config_path: Path to config file. If None, searches for .nilcoderc or .nilcode.json
        """
        self.config = DEFAULT_CONFIG.copy()
        self.config_file = None

        if config_path:
            self.load_from_file(config_path)
        else:
            self.discover_and_load()

    def discover_and_load(self) -> bool:
        """
        Discover and load configuration from current directory.

        Returns:
            True if config was found and loaded
        """
        # Try different config file names
        config_names = ['.nilcoderc', '.nilcode.json', 'nilcode.json']
        
        for config_name in config_names:
            config_path = Path.cwd() / config_name
            if config_path.exists():
                return self.load_from_file(str(config_path))
        
        # Check parent directories (up to 3 levels)
        current = Path.cwd()
        for _ in range(3):
            current = current.parent
            for config_name in config_names:
                config_path = current / config_name
                if config_path.exists():
                    return self.load_from_file(str(config_path))
        
        return False

    def load_from_file(self, config_path: str) -> bool:
        """
        Load configuration from a file.

        Args:
            config_path: Path to config file

        Returns:
            True if loaded successfully
        """
        try:
            path = Path(config_path)
            if not path.exists():
                return False

            with open(path, 'r', encoding='utf-8') as f:
                user_config = json.load(f)

            # Deep merge with defaults
            self._deep_merge(self.config, user_config)
            self.config_file = str(path)
            
            return True
        except Exception as e:
            print(f"Warning: Failed to load config from {config_path}: {e}")
            return False

    def save_to_file(self, config_path: Optional[str] = None) -> bool:
        """
        Save configuration to a file.

        Args:
            config_path: Path to save config. If None, uses current config_file

        Returns:
            True if saved successfully
        """
        try:
            if config_path is None:
                config_path = self.config_file or '.nilcoderc'

            path = Path(config_path)
            with open(path, 'w', encoding='utf-8') as f:
                json.dump(self.config, f, indent=2)

            self.config_file = str(path)
            return True
        except Exception as e:
            print(f"Error: Failed to save config to {config_path}: {e}")
            return False

    def get(self, key: str, default: Any = None) -> Any:
        """
        Get a configuration value.

        Args:
            key: Config key (supports dot notation, e.g., 'agent_settings.planner.temperature')
            default: Default value if key not found

        Returns:
            Configuration value
        """
        keys = key.split('.')
        value = self.config
        
        for k in keys:
            if isinstance(value, dict) and k in value:
                value = value[k]
            else:
                return default
        
        return value

    def set(self, key: str, value: Any):
        """
        Set a configuration value.

        Args:
            key: Config key (supports dot notation)
            value: Value to set
        """
        keys = key.split('.')
        config = self.config
        
        for k in keys[:-1]:
            if k not in config:
                config[k] = {}
            config = config[k]
        
        config[keys[-1]] = value

    def get_agent_settings(self, agent_name: str) -> Dict[str, Any]:
        """
        Get settings for a specific agent.

        Args:
            agent_name: Name of the agent

        Returns:
            Agent settings dictionary
        """
        return self.get(f'agent_settings.{agent_name}', {})

    def get_ignore_patterns(self) -> List[str]:
        """
        Get file ignore patterns.

        Returns:
            List of glob patterns to ignore
        """
        return self.get('ignore_patterns', [])

    def should_ignore_file(self, file_path: str) -> bool:
        """
        Check if a file should be ignored based on patterns.

        Args:
            file_path: Path to check

        Returns:
            True if file should be ignored
        """
        from fnmatch import fnmatch
        
        patterns = self.get_ignore_patterns()
        path_str = str(file_path)
        
        for pattern in patterns:
            if fnmatch(path_str, pattern):
                return True
        
        return False

    def _deep_merge(self, base: dict, updates: dict):
        """
        Deep merge updates into base dictionary.

        Args:
            base: Base dictionary to merge into
            updates: Updates to merge
        """
        for key, value in updates.items():
            if key in base and isinstance(base[key], dict) and isinstance(value, dict):
                self._deep_merge(base[key], value)
            else:
                base[key] = value

    def create_default_config(self, path: str = '.nilcoderc') -> bool:
        """
        Create a default configuration file.

        Args:
            path: Path where to create the config file

        Returns:
            True if created successfully
        """
        try:
            config_path = Path(path)
            if config_path.exists():
                return False

            with open(config_path, 'w', encoding='utf-8') as f:
                json.dump(DEFAULT_CONFIG, f, indent=2)

            print(f"Created default configuration at {path}")
            return True
        except Exception as e:
            print(f"Error: Failed to create config at {path}: {e}")
            return False


# Global config instance
_global_config: Optional[NilCodeConfig] = None


def get_config() -> NilCodeConfig:
    """
    Get the global configuration instance.

    Returns:
        NilCodeConfig instance
    """
    global _global_config
    if _global_config is None:
        _global_config = NilCodeConfig()
    return _global_config


def load_config(config_path: Optional[str] = None) -> NilCodeConfig:
    """
    Load configuration from file or discover it.

    Args:
        config_path: Optional path to config file

    Returns:
        NilCodeConfig instance
    """
    global _global_config
    _global_config = NilCodeConfig(config_path)
    return _global_config

