"""
Multi-Agent Development System

A LangChain-based multi-agent system for software development tasks.
"""

import os

from .main_agent import MultiAgentSystem, create_agent_system

__version__ = "2.0.23"
file = os.path.abspath(__file__)

__all__ = [
    "MultiAgentSystem",
    "create_agent_system",
]
