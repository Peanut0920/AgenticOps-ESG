import random
from src.core.base_agent import BaseAgent
from src.core.state import AgenticOpsState
from src.utils.ml_forecast import forecast_optimal_allocation

class RightSizingAgent(BaseAgent):
    """
    Generates autonomous right-sizing proposals for underutilized VMs.
    Uses ML forecasting to suggest new CPU/memory limits while calculating
    carbon savings and risk scores.
    """

    def __init__(self):
        super().__init__(agent_id="RightSizing-Engine")

    def process(self, state: AgenticOpsState) -> AgenticOpsState:
        candidates = []
        grid_carbon = state["raw_telemetry"].get("grid_carbon_intensity", 0.58)
        digital_twin = state.get("digital_twin", {})
        
        for vm in digital_twin.get("overprovisioned_vms", []):
            # Simulate ML forecasting based on historical usage
            forecast = forecast_optimal_allocation(vm.get("history", [50, 52, 48]), horizon_hours=72)
            
            # Calculate energy saved over 72 hours (Watts * hours / 1000 = kWh)
            energy_saved_kwh = (vm["current_power"] - forecast.optimal_power) * 72 / 1000
            carbon_saved_kg = energy_saved_kwh * grid_carbon
            
            candidates.append({
                "agent_source": "RightSizingAgent",
                "action": "resize",
                "vm_id": vm["id"],
                "new_cpu_limits": f"{forecast.cpu_millicores}m",
                "new_ram_gb": f"{forecast.ram_gb}Gi",
                "carbon_saving_kg": round(max(0, carbon_saved_kg), 2),
                "risk_score": round(forecast.steal_probability, 1),  # CPU contention risk
                "performance_delta": round(random.uniform(0.75, 0.98), 2),  # Performance impact
                "energy_saved_kwh": round(energy_saved_kwh, 2)
            })
        
        # Append to existing proposed actions
        state["proposed_actions"].extend(candidates)
        self._log(state, f"📉 Generated {len(candidates)} right-sizing proposals.")
        return state