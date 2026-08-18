import pytest
from unittest.mock import patch
from src.orchestrator.main import Orchestrator
from src.core.state import AgenticOpsState

@patch("src.orchestrator.main.TelemetryCollectorAgent")
@patch("src.orchestrator.main.RightSizingAgent")
@patch("src.orchestrator.main.PredictiveRefreshAgent")
@patch("src.orchestrator.main.ComplianceValidatorAgent")
@patch("src.orchestrator.main.ParetoOptimizationAgent")
@patch("src.orchestrator.main.ExecutionAgent")
@patch("src.orchestrator.main.ESGReportingAgent")
def test_orchestrator_full_cycle(mock_report, mock_exec, mock_opt, mock_comp, mock_refresh, mock_right, mock_tele):
    """Test that orchestrator runs all agents and returns a final state."""
    # Mock each agent's process to return the state unchanged (or with minimal modifications)
    def mock_process(state):
        state["audit_trail"].append("mock processed")
        return state

    mock_tele.return_value.process = mock_process
    mock_right.return_value.process = mock_process
    mock_refresh.return_value.process = mock_process
    mock_comp.return_value.process = mock_process
    mock_opt.return_value.process = mock_process
    mock_exec.return_value.process = mock_process
    mock_report.return_value.process = mock_process

    orch = Orchestrator()
    final_state = orch.run_full_cycle("test goal")

    assert final_state["session_id"] is not None
    assert len(final_state["audit_trail"]) >= 7  # at least one per agent
    assert "esg_report_packet" in final_state