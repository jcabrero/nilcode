"""
Multi-Agent Development System

A LangChain-based multi-agent system for software development tasks.
"""

from .main_agent import MultiAgentSystem, create_agent_system

__version__ = "0.1.0"

__all__ = [
    "MultiAgentSystem",
    "create_agent_system",
]
