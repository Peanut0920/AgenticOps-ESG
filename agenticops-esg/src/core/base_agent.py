from abc import ABC, abstractmethod
from datetime import datetime
from typing import TYPE_CHECKING

# Avoid circular imports by using TYPE_CHECKING for the state type hint
if TYPE_CHECKING:
    from .state import AgenticOpsState

class BaseAgent(ABC):
    """
    Abstract Base Class for all autonomous agents in the system.

    Every agent (Telemetry, Rightsizing, Refresh, Compliance, Optimize, 
    Execution, Reporting) must inherit from this class and implement 
    the `process` method.

    The `_log` utility ensures every state mutation is cryptographically 
    traceable in the audit trail.
    """

    def __init__(self, agent_id: str):
        """
        Initializes the agent with a unique identifier.

        Args:
            agent_id: Human-readable name (e.g., "RightSizing-Engine").
        """
        self.agent_id = agent_id

    @abstractmethod
    def process(self, state: "AgenticOpsState") -> "AgenticOpsState":
        """
        The main execution hook for the agent.

        This method accepts the current immutable state, performs its specific
        function (e.g., analyzing telemetry, generating resize proposals), 
        mutates the relevant fields, and returns the updated state.

        Important: The state is passed by reference (dict), but we treat it as
        immutable by convention—agents should only add new keys/entries, not 
        delete existing audit trails.

        Args:
            state: The current AgenticOpsState object.

        Returns:
            The modified AgenticOpsState object for the next agent in the pipeline.
        """
        pass

    def _log(self, state: "AgenticOpsState", message: str) -> None:
        """
        Appends a timestamped, agent-stamped log entry to the audit trail.

        This is the primary mechanism for regulatory compliance, as it creates
        a verifiable chain of custody for every infrastructure decision.

        Args:
            state: The current state object (will be mutated in-place with the log).
            message: The descriptive log message (e.g., "Found 5 overprovisioned VMs.").
        """
        timestamp = datetime.now().isoformat(timespec="milliseconds")
        log_entry = f"[{timestamp}] [{self.agent_id}] {message}"
        
        # Ensure the audit trail list exists before appending
        if "audit_trail" in state:
            state["audit_trail"].append(log_entry)
        else:
            # Fallback safety (should not happen if state is initialized correctly)
            state["audit_trail"] = [log_entry]