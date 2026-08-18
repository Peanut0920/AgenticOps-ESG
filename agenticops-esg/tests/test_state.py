import pytest
from src.core.state import AgenticOpsState

def test_state_creation():
    """Verify that a minimal state can be created with all required keys."""
    state: AgenticOpsState = {
        "session_id": "abc-123",
        "user_goal": "reduce carbon",
        "raw_telemetry": {},
        "digital_twin": {},
        "proposed_actions": [],
        "compliance_violations": [],
        "approved_execution_plan": {},
        "audit_trail": [],
        "esg_report_packet": {}
    }
    assert state["session_id"] == "abc-123"
    assert isinstance(state["audit_trail"], list)