from src.core.base_agent import BaseAgent
from src.core.state import AgenticOpsState

class ParetoOptimizationAgent(BaseAgent):
    """
    Multi-objective optimizer.
    Scores each proposed action based on Performance, Carbon Savings, and Risk,
    then selects the top 5 actions with the highest utility score.
    """

    def __init__(self):
        super().__init__(agent_id="Pareto-Scorer")
        # Weights for (Performance, Carbon, Risk)
        self.weights = (0.4, 0.35, 0.25)

    def process(self, state: AgenticOpsState) -> AgenticOpsState:
        scored_actions = []
        
        for action in state.get("proposed_actions", []):
            # Normalize metrics
            perf = action.get("performance_delta", 0.5)  # 0.5 to 1.25
            # Normalize carbon: assume 100 kg is the max expected saving in a single action
            carbon = min(action.get("carbon_saving_kg", 0) / 50, 1.0)  
            risk = 1 - min(action.get("risk_score", 0) / 100, 1.0)  # Lower risk = higher score
            
            utility = (self.weights[0] * perf) + (self.weights[1] * carbon) + (self.weights[2] * risk)
            action["utility_score"] = round(utility, 4)
            scored_actions.append(action)
        
        # Sort descending by utility
        scored_actions.sort(key=lambda x: x["utility_score"], reverse=True)
        
        # Keep only the top 5 to prevent excessive infrastructure changes (thrashing)
        state["proposed_actions"] = scored_actions[:5]
        
        self._log(state, f"🎯 Optimized to top {len(state['proposed_actions'])} actions by utility score.")
        return state