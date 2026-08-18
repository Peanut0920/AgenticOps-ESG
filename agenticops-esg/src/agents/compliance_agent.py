from src.core.base_agent import BaseAgent
from src.core.state import AgenticOpsState
from src.utils.db_connectors import VectorDatabase

class ComplianceValidatorAgent(BaseAgent):
    """
    The regulatory gatekeeper.
    Uses RAG to retrieve legal clauses and flags/drops actions that violate
    data sovereignty (MCMC), climate risk (Bursa), or operational resilience.
    """

    def __init__(self):
        super().__init__(agent_id="Compliance-Gatekeeper")
        self.retriever = VectorDatabase()

    def process(self, state: AgenticOpsState) -> AgenticOpsState:
        violations = []
        valid_actions = []
        
        for action in state.get("proposed_actions", []):
            is_valid = True
            
            # --- Rule 1: MCMC Data Residency (Section 5.2) ---
            # All data must remain in MY-01 region.
            # Simulated check: if the VM/host name doesn't contain "kl-dc", flag it.
            asset_id = action.get("vm_id") or action.get("host_id") or ""
            if "kl-dc" not in asset_id.lower():
                clause = self.retriever.similarity_search("mcmc_data_sovereignty")
                violations.append(f"{asset_id}: {clause[0].text}")
                is_valid = False
            
            # --- Rule 2: Bursa Climate Risk (Operational Resilience) ---
            # If a resize has risk_score > 15%, it violates Bursa's TCFD guidelines.
            if action.get("risk_score", 0) > 15.0:
                clause = self.retriever.similarity_search("bursa_tcfd_risk")
                violations.append(f"{asset_id}: {clause[0].text}")
                is_valid = False
            
            # If valid, keep it
            if is_valid:
                valid_actions.append(action)
        
        # Update state
        state["compliance_violations"] = violations
        state["proposed_actions"] = valid_actions
        
        self._log(state, f"⚖️ Compliance check complete. {len(violations)} violations found. "
                         f"{len(valid_actions)} actions passed.")
        return state