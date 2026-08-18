"""
Main Orchestrator for AgenticOps-ESG.
Responsible for instantiating all agents and executing the full workflow pipeline.
"""

import uuid
from typing import Optional
from src.core.state import AgenticOpsState
from src.agents.telemetry_agent import TelemetryCollectorAgent
from src.agents.rightsizing_agent import RightSizingAgent
from src.agents.refresh_agent import PredictiveRefreshAgent
from src.agents.compliance_agent import ComplianceValidatorAgent
from src.agents.optimize_agent import ParetoOptimizationAgent
from src.agents.execution_agent import ExecutionAgent
from src.agents.reporting_agent import ESGReportingAgent
from src.utils.logger import logger

class Orchestrator:
    """
    The main engine that chains all autonomous agents together.
    
    The pipeline order is fixed and ensures that each agent has the necessary
    context from the previous ones:
    1. Telemetry -> 2. RightSizing -> 3. Refresh -> 4. Compliance ->
    5. Optimize -> 6. Execution -> 7. Reporting
    """

    def __init__(self):
        """Initializes all 7 agents with their dependencies."""
        logger.info("🚀 Initializing AgenticOps-ESG Orchestrator...")
        
        self.telemetry = TelemetryCollectorAgent()
        self.rightsizer = RightSizingAgent()
        self.refresher = PredictiveRefreshAgent()
        self.compliance = ComplianceValidatorAgent()
        self.optimizer = ParetoOptimizationAgent()
        self.executor = ExecutionAgent()
        self.reporter = ESGReportingAgent()
        
        logger.info("✅ All 7 agents instantiated successfully.")

    def run_full_cycle(self, goal: str = "Optimize infrastructure for lowest carbon intensity") -> AgenticOpsState:
        """
        Executes the complete agent pipeline from scratch.
        
        Args:
            goal: The high-level human objective (e.g., "Reduce PUE to 1.3").
            
        Returns:
            The final AgenticOpsState containing the ESG report packet and audit trail.
        """
        logger.info(f"🔄 Starting full workflow cycle with goal: '{goal}'")
        
        # Initialize a fresh state
        state: AgenticOpsState = {
            "session_id": str(uuid.uuid4()),
            "user_goal": goal,
            "raw_telemetry": {},
            "digital_twin": {},
            "proposed_actions": [],
            "compliance_violations": [],
            "approved_execution_plan": {},
            "audit_trail": [],
            "esg_report_packet": {}
        }
        
        # Execute the sequential pipeline
        logger.info(f"📡 Step 1/7: Telemetry Collection")
        state = self.telemetry.process(state)
        
        logger.info(f"📉 Step 2/7: Right-Sizing Analysis")
        state = self.rightsizer.process(state)
        
        logger.info(f"🔄 Step 3/7: Predictive Refresh Planning")
        state = self.refresher.process(state)
        
        logger.info(f"⚖️ Step 4/7: Compliance Validation")
        state = self.compliance.process(state)
        
        logger.info(f"🎯 Step 5/7: Pareto Optimization")
        state = self.optimizer.process(state)
        
        logger.info(f"🚀 Step 6/7: Execution (GitOps + ERP)")
        state = self.executor.process(state)
        
        logger.info(f"📄 Step 7/7: ESG Reporting")
        state = self.reporter.process(state)
        
        logger.info(f"✅ Full workflow complete. Session ID: {state['session_id']}. "
                    f"Actions proposed: {len(state['proposed_actions'])}. "
                    f"Audit entries: {len(state['audit_trail'])}.")
        return state

    def run_initial_discovery(self) -> AgenticOpsState:
        """
        Lightweight run that performs a full cycle but with a default discovery goal.
        Used to populate the dashboard on startup.
        """
        return self.run_full_cycle("Initial discovery and telemetry ingestion")

    def execute_single_action(self, action: dict) -> AgenticOpsState:
        """
        Executes a specific approved action without re-running the entire pipeline.
        
        In a production system, this would target only the Execution Agent.
        For simplicity in this demo, we re-run the full cycle but preserve the
        action as already approved.
        
        Args:
            action: The pre-approved action dictionary.
            
        Returns:
            The updated state after execution.
        """
        logger.info(f"⚡ Executing single approved action: {action.get('action', 'unknown')} on {action.get('vm_id', action.get('host_id', 'unknown'))}")
        
        # Run a full cycle to refresh context, but mark this action as approved
        state = self.run_full_cycle("Executing approved action")
        
        # Ensure the action is in the proposed list (or we could just execute directly)
        # For demo, we log it and let the executor handle it.
        for a in state["proposed_actions"]:
            if a.get("vm_id") == action.get("vm_id") or a.get("host_id") == action.get("host_id"):
                a["approved_status"] = "APPROVED"
        
        # Re-run execution to apply it
        state = self.executor.process(state)
        state = self.reporter.process(state)
        
        return state