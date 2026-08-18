"""
Core module for AgenticOps-ESG.
Provides the base agent abstraction and the shared state contract.
"""
from .state import AgenticOpsState
from .base_agent import BaseAgent

__all__ = [
    "AgenticOpsState",
    "BaseAgent"
]