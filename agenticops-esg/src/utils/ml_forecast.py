"""
Machine Learning utilities for forecasting and hardware degradation analysis.
Contains mock implementations for demo purposes.
"""

import random
from typing import Dict, Any, List, Optional
from dataclasses import dataclass

# -------------------- Data Classes for Forecast Outputs --------------------

@dataclass
class ForecastResult:
    """Result container for VM allocation forecasting."""
    cpu_millicores: int
    ram_gb: int
    optimal_power: float
    steal_probability: float  # Probability of CPU contention if downsized

@dataclass
class DegradationCurve:
    """Result container for hardware degradation analysis."""
    extra_kwh_per_year: float
    crossover_quarter: str

# -------------------- Mock Forecasting Functions --------------------

def forecast_optimal_allocation(history: List[float], horizon_hours: int = 72) -> ForecastResult:
    """
    Simulates a time-series forecast for CPU/Memory usage.

    In production, this would use Neural Prophet or LightGBM to predict
    future resource requirements based on historical usage patterns.

    Args:
        history: Historical CPU/Memory utilization values.
        horizon_hours: How far ahead to forecast.

    Returns:
        ForecastResult with recommended limits and risk score.
    """
    # Simulate intelligence: recommend a reduction based on current average
    avg_util = sum(history) / len(history) if history else 50
    
    if avg_util < 30:
        reduction_factor = 0.5  # Aggressive downsize
    elif avg_util < 50:
        reduction_factor = 0.7
    else:
        reduction_factor = 0.9  # Conservative
    
    base_cpu = random.randint(1500, 2500)  # millicores
    base_ram = random.randint(8, 32)       # GB
    
    return ForecastResult(
        cpu_millicores=int(base_cpu * reduction_factor),
        ram_gb=int(base_ram * reduction_factor),
        optimal_power=base_cpu * reduction_factor * 0.2,  # Rough power scaling
        steal_probability=round(random.uniform(2, 14), 1)  # Under 15% is safe
    )

def calculate_degradation_curve(age_months: int, model_sku: str = "Dell_R760") -> DegradationCurve:
    """
    Simulates a Physics-of-Failure (PoF) degradation curve for server hardware.

    Calculates the additional energy waste caused by aging components
    (e.g., less efficient power supplies, thermal throttling).

    Args:
        age_months: Age of the hardware in months.
        model_sku: Hardware SKU (used to look up base specs).

    Returns:
        DegradationCurve with annual energy waste and crossover quarter.
    """
    # Degradation accelerates with age
    base_waste = 20  # kWh per year baseline at 24 months
    age_factor = (age_months / 36) ** 1.5  # Exponential degradation
    extra_kwh = base_waste * age_factor + random.uniform(-10, 10)
    
    return DegradationCurve(
        extra_kwh_per_year=round(max(10, extra_kwh), 2),
        crossover_quarter=calc_crossover_point(age_months)
    )

def calc_crossover_point(age_months: int) -> str:
    """
    Determines the optimal refresh quarter based on the current age.

    The crossover point is when the cumulative energy waste exceeds
    the embodied carbon of a new unit.

    Args:
        age_months: Current age of the hardware.

    Returns:
        str: The projected quarter (e.g., "Q3-2027") for full replacement.
    """
    if age_months < 30:
        return "Q4-2027"
    elif age_months < 42:
        return "Q2-2027"
    else:
        return "Q1-2027"