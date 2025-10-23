"""
A2A Integration Module

This module provides integration with external agents via the A2A protocol.
"""

from .registry import (
    A2AAgentRegistry,
    ExternalAgent,
    get_global_registry,
    initialize_registry_from_config
)

__all__ = [
    'A2AAgentRegistry',
    'ExternalAgent',
    'get_global_registry',
    'initialize_registry_from_config',
]
