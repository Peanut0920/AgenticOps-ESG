"""
Dependency injection container for the AgenticOps-ESG API.
"""

from src.orchestrator.main import Orchestrator

# Singleton orchestrator instance
_orchestrator: Orchestrator = None

def get_orchestrator() -> Orchestrator:
    """
    Returns the global Orchestrator singleton.
    Creates it if it doesn't exist.
    """
    global _orchestrator
    if _orchestrator is None:
        _orchestrator = Orchestrator()
    return _orchestrator