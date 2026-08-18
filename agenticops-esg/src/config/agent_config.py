"""
Agent configuration loader.
Parses the agent_config.yaml file and returns structured dataclasses.
"""

import os
import yaml
from dataclasses import dataclass
from typing import List, Dict, Any, Optional
from pathlib import Path

# -------------------- Configuration Dataclasses --------------------

@dataclass
class ParetoWeights:
    """Weights for multi-objective optimization."""
    performance: float = 0.4
    carbon: float = 0.35
    risk: float = 0.25

@dataclass
class Thresholds:
    """Threshold values for triggering actions."""
    cpu_underutilization_pct: float = 40.0
    ram_underutilization_pct: float = 50.0
    risk_max_pct: float = 15.0
    drive_fail_threshold: float = 0.7
    pue_target: float = 1.4
    min_carbon_saving_kg: float = 0.5

@dataclass
class Schedules:
    """Cron-like scheduling for agent execution."""
    telemetry_interval_seconds: int = 300
    rightsizing_interval_hours: int = 6
    refresh_interval_hours: int = 24
    reporting_interval_days: int = 7

@dataclass
class AgentConfig:
    """Complete agent configuration container."""
    weights: ParetoWeights
    thresholds: Thresholds
    schedules: Schedules
    max_actions_per_cycle: int = 5
    auto_approve_allowed_actions: List[str] = None  # e.g., ["resize"]
    
    def __post_init__(self):
        if self.auto_approve_allowed_actions is None:
            self.auto_approve_allowed_actions = []

# -------------------- YAML Loader --------------------

def load_agent_config(config_path: Optional[str] = None) -> AgentConfig:
    """
    Loads the agent configuration from a YAML file.
    
    Args:
        config_path: Path to the YAML file. If None, uses default path.
        
    Returns:
        AgentConfig dataclass instance.
    """
    if config_path is None:
        # Default path: src/config/agent_config.yaml
        current_dir = Path(__file__).parent
        config_path = current_dir / "agent_config.yaml"
    
    # Load YAML
    with open(config_path, "r", encoding="utf-8") as f:
        raw = yaml.safe_load(f)
    
    # Parse into dataclasses
    weights = ParetoWeights(**raw.get("pareto_weights", {}))
    thresholds = Thresholds(**raw.get("thresholds", {}))
    schedules = Schedules(**raw.get("schedules", {}))
    
    return AgentConfig(
        weights=weights,
        thresholds=thresholds,
        schedules=schedules,
        max_actions_per_cycle=raw.get("max_actions_per_cycle", 5),
        auto_approve_allowed_actions=raw.get("auto_approve_allowed_actions", [])
    )

# Singleton instance for easy import
config = load_agent_config()