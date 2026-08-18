import pytest
from unittest.mock import patch
from src.agents.compliance_agent import ComplianceValidatorAgent
from src.core.state import AgenticOpsState

@patch("src.agents.compliance_agent.VectorDatabase")
def test_compliance_agent_filters_violations(mock_vector_db):
    """Test that compliance agent removes actions with violations."""
    # Mock the RAG retrieval to return dummy clauses
    mock_db_instance = mock_vector_db.return_value
    mock_db_instance.similarity_search.return_value = [
        type('Doc', (), {'text': 'Mock violation text'})()
    ]

    agent = ComplianceValidatorAgent()
    state: AgenticOpsState = {
        "session_id": "test",
        "user_goal": "test",
        "raw_telemetry": {},
        "digital_twin": {},
        "proposed_actions": [
            {"action": "resize", "vm_id": "some-other-region", "risk_score": 10},
            {"action": "resize", "vm_id": "kl-dc-valid", "risk_score": 5}
        ],
        "compliance_violations": [],
        "approved_execution_plan": {},
        "audit_trail": [],
        "esg_report_packet": {}
    }
    new_state = agent.process(state)

    # Only the second action should pass (first is invalid due to region)
    assert len(new_state["proposed_actions"]) == 1
    assert new_state["proposed_actions"][0]["vm_id"] == "kl-dc-valid"
    assert len(new_state["compliance_violations"]) == 1