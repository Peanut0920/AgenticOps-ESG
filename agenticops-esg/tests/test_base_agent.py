import pytest
from src.core.base_agent import BaseAgent
from src.core.state import AgenticOpsState

class ConcreteAgent(BaseAgent):
    """Concrete implementation for testing."""
    def process(self, state):
        self._log(state, "Test log message")
        state["test_field"] = "success"
        return state

def test_base_agent_instantiation():
    """Verify that a concrete subclass can be instantiated."""
    agent = ConcreteAgent("test-agent")
    assert agent.agent_id == "test-agent"

def test_base_agent_process():
    """Verify that process mutates state and logs correctly."""
    agent = ConcreteAgent("test-agent")
    state: AgenticOpsState = {
        "session_id": "test",
        "user_goal": "test",
        "raw_telemetry": {},
        "digital_twin": {},
        "proposed_actions": [],
        "compliance_violations": [],
        "approved_execution_plan": {},
        "audit_trail": [],
        "esg_report_packet": {}
    }
    new_state = agent.process(state)
    assert new_state["test_field"] == "success"
    assert len(new_state["audit_trail"]) == 1
    assert "[test-agent]" in new_state["audit_trail"][0]