from src.core.base_agent import BaseAgent
from src.core.state import AgenticOpsState
from src.utils.db_connectors import VectorDatabase
from src.utils.ml_forecast import calculate_degradation_curve, calc_crossover_point
import random

class PredictiveRefreshAgent(BaseAgent):
    """
    Determines whether to fully replace aging hardware, partially repair it,
    or defer the refresh based on a carbon-based crossover analysis.
    """

    def __init__(self):
        super().__init__(agent_id="Refresh-Planner")
        self.rag_db = VectorDatabase()  # For retrieving embodied carbon data

    def process(self, state: AgenticOpsState) -> AgenticOpsState:
        candidates = []
        digital_twin = state.get("digital_twin", {})
        
        for host in digital_twin.get("aging_hardware", []):
            # 1. Retrieve embodied carbon from RAG (mock)
            doc = self.rag_db.similarity_search(host["model_sku"])
            embodied_carbon = doc[0].metadata.get("embodied_kg_co2", 850)
            
            # 2. Calculate degradation curve (energy waste due to aging)
            age = host.get("age_months", 36)
            degradation = calculate_degradation_curve(age, host["model_sku"])
            wasted_energy_annual = degradation.extra_kwh_per_year
            
            # 3. Crossover Decision:
            # If 5 years of energy waste > 80% of embodied carbon, recommend full refresh.
            # Otherwise, recommend partial repair (e.g., replace SSDs/RAM).
            if (wasted_energy_annual * 5) > (embodied_carbon * 0.8):
                candidates.append({
                    "agent_source": "PredictiveRefreshAgent",
                    "action": "full_refresh",
                    "host_id": host["id"],
                    "crossover_quarter": calc_crossover_point(age),
                    "embodied_carbon_kg": embodied_carbon,
                    "annual_energy_waste": wasted_energy_annual,
                    "carbon_saving_kg": embodied_carbon * 0.3,  # Avoided future waste
                    "performance_delta": 1.25  # New hardware much faster
                })
            else:
                # Partial repair: much cheaper, lower carbon impact
                candidates.append({
                    "agent_source": "PredictiveRefreshAgent",
                    "action": "partial_repair",
                    "host_id": host["id"],
                    "recommendation": "Replace only SSDs and RAM modules",
                    "capex_saving": round(random.uniform(30000, 60000), 2),
                    "ewaste_avoided_kg": round(random.uniform(10, 25), 2),
                    "carbon_saving_kg": round(random.uniform(2, 8), 2),
                    "performance_delta": 0.95
                })
        
        state["proposed_actions"].extend(candidates)
        self._log(state, f"🔄 Analyzed {len(candidates)} hardware refresh candidates.")
        return state