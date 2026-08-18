from datetime import datetime
from src.core.base_agent import BaseAgent
from src.core.state import AgenticOpsState
from src.utils.api_clients import mock_github_pr, mock_erp_requisition

class ExecutionAgent(BaseAgent):
    """
    The execution layer.
    Converts approved actions into GitOps PRs (for resizes) and ERP requisitions
    (for full hardware refreshes). All changes are tagged with the audit session ID.
    """

    def __init__(self):
        super().__init__(agent_id="Executor")

    def process(self, state: AgenticOpsState) -> AgenticOpsState:
        plan = {"resizes": [], "refresh_prs": [], "repairs": []}
        session_id = state.get("session_id", "unknown-session")
        
        for action in state.get("proposed_actions", []):
            if action["action"] == "resize":
                # Generate a Kubernetes VerticalPodAutoscaler (VPA) patch
                patch = f"""
apiVersion: autoscaling.k8s.io/v1
kind: VerticalPodAutoscaler
metadata:
  name: {action['vm_id']}-autofix
  annotations:
    agenticops-session: {session_id}
spec:
  targetRef:
    apiVersion: apps/v1
    kind: Deployment
    name: {action['vm_id']}
  resourcePolicy:
    containerPolicies:
    - containerName: '*'
      minAllowed:
        cpu: {action['new_cpu_limits']}
        memory: {action['new_ram_gb']}
"""
                pr_url = mock_github_pr(
                    repo="infra-as-code",
                    branch=f"autofix-{action['vm_id']}-{datetime.now().strftime('%Y%m%d')}",
                    content=patch,
                    commit_msg=f"[AgenticOps] Resize {action['vm_id']} to save {action.get('carbon_saving_kg', 0)}kg CO2e"
                )
                plan["resizes"].append({
                    "vm": action['vm_id'],
                    "pr_url": pr_url,
                    "carbon_saved": action.get("carbon_saving_kg", 0)
                })
                
            elif action["action"] == "full_refresh":
                erp_id = mock_erp_requisition(
                    sku="Dell_R760",
                    quantity=1,
                    just=f"Crossover reached: {action.get('crossover_quarter', 'Q4-2026')} | Session: {session_id}"
                )
                plan["refresh_prs"].append({
                    "host": action['host_id'],
                    "erp_requisition": erp_id,
                    "embodied_carbon": action.get("embodied_carbon_kg", 850)
                })
                
            elif action["action"] == "partial_repair":
                # For repairs, just log the recommendation (or raise a ticket)
                plan["repairs"].append({
                    "host": action['host_id'],
                    "recommendation": action.get("recommendation", "Replace SSDs"),
                    "capex_saving": action.get("capex_saving", 0)
                })
        
        state["approved_execution_plan"] = plan
        self._log(state, f"🚀 Executed: {len(plan['resizes'])} resizes, "
                         f"{len(plan['refresh_prs'])} full refreshes, "
                         f"{len(plan['repairs'])} repairs logged.")
        return state