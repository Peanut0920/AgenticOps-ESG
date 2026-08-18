import random
from src.core.base_agent import BaseAgent
from src.core.state import AgenticOpsState
from src.utils.api_clients import mock_prometheus_query, mock_tnb_api

class TelemetryCollectorAgent(BaseAgent):
    """
    The first agent in the pipeline.
    Scrapes telemetry (CPU, power, drive health) from Prometheus/DCIM,
    fetches grid carbon intensity from TNB, and builds a structured Digital Twin.
    """

    def __init__(self):
        super().__init__(agent_id="Telemetry-Ingestor")

    def process(self, state: AgenticOpsState) -> AgenticOpsState:
        # 1. Scrape hardware metrics (mock for demo)
        metrics = mock_prometheus_query("node_cpu,node_power,smart_drive")
        
        # 2. Fetch current grid carbon intensity from TNB API (mock)
        grid_carbon = mock_tnb_api()
        
        # 3. Store raw telemetry
        state["raw_telemetry"] = {
            "metrics": metrics,
            "grid_carbon_intensity": grid_carbon,
            "scrape_timestamp": __import__('datetime').datetime.now().isoformat()
        }
        
        # 4. Build the Digital Twin (pre-processed datasets for downstream agents)
        digital_twin = {
            # Identify overprovisioned VMs (CPU < 40% and RAM < 50%)
            "overprovisioned_vms": [
                {
                    "id": m["instance"],
                    "current_power": m["power_draw_watts"],
                    "cpu_pct": m["cpu_util_pct"],
                    "ram_util_gb": m["ram_util_gb"],
                    "history": [random.uniform(20, m["cpu_util_pct"] + 10) for _ in range(24)]  # Simulated 24hr history
                }
                for m in metrics 
                if m["cpu_util_pct"] < 40 and m["ram_util_gb"] < 64
            ],
            # Identify aging hardware (drive fail prob > 0.7 or random selection)
            "aging_hardware": [
                {
                    "id": m["instance"],
                    "model_sku": "Dell_R760",
                    "age_months": random.randint(24, 54),
                    "drive_fail_prob": m["drive_fail_prob"],
                    # We store a callable-like object but use a dict to avoid lambda pickling issues
                    "degradation_data": {"extra_kwh_per_year": 150, "crossover": "Q1-2027"}
                }
                for m in metrics 
                if m["drive_fail_prob"] > 0.7 or random.random() > 0.7  # Simulate aging
            ],
            "current_pue": round(1.4 + random.uniform(0, 0.12), 3),
            "recycled_kg": random.randint(5, 45)
        }
        state["digital_twin"] = digital_twin
        
        self._log(state, f"✅ Ingested {len(metrics)} assets. Grid intensity: {grid_carbon} kg/kWh. "
                         f"Found {len(digital_twin['overprovisioned_vms'])} overprovisioned VMs, "
                         f"{len(digital_twin['aging_hardware'])} aging hosts.")
        return state