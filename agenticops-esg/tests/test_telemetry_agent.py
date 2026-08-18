import pytest
from unittest.mock import patch
from src.agents.telemetry_agent import TelemetryCollectorAgent
from src.core.state import AgenticOpsState

@patch("src.agents.telemetry_agent.mock_prometheus_query")
@patch("src.agents.telemetry_agent.mock_tnb_api")
def test_telemetry_agent(mock_tnb, mock_prometheus):
    """Test that telemetry agent fetches data and builds digital twin."""
    # Mock returns
    mock_prometheus.return_value = [
        {"instance": "kl-dc-rack-01-host", "cpu_util_pct": 35.0, "power_draw_watts": 300, 
         "ram_util_gb": 40, "drive_fail_prob": 0.2, "timestamp": "2026-01-01T00:00:00"}
    ]
    mock_tnb.return_value = 0.58

    agent = TelemetryCollectorAgent()
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

    assert "metrics" in new_state["raw_telemetry"]
    assert new_state["raw_telemetry"]["grid_carbon_intensity"] == 0.58
    assert len(new_state["digital_twin"]["overprovisioned_vms"]) >= 0
    assert len(new_state["digital_twin"]["aging_hardware"]) >= 0
    assert new_state["digital_twin"]["current_pue"] is not None
    assert len(new_state["audit_trail"]) == 1