"""
API Clients for external integrations.
Includes both mock (for demo/development) and real wrappers.
"""

import random
import time
from datetime import datetime, timedelta
from typing import List, Dict, Any, Optional

# -------------------- MOCK DATA GENERATORS --------------------

def mock_prometheus_query(query: str) -> List[Dict[str, Any]]:
    """
    Simulates a Prometheus instant vector query response.
    Returns realistic telemetry for 10 virtual hosts in a Malaysian data center.

    Args:
        query: The PromQL query string (ignored in mock).

    Returns:
        List of metric dictionaries with instance, CPU, power, RAM, and disk health.
    """
    hosts = [f"kl-dc-rack-{i:02d}-host" for i in range(1, 11)]
    data = []
    for host in hosts:
        # Simulate realistic variance
        cpu = round(random.uniform(15, 92), 1)  # Most VMs are underutilized
        power = round(150 + (cpu / 100) * 450, 1)  # Power scales with CPU
        ram_gb = round(random.uniform(8, 128), 1)
        drive_fail = round(random.uniform(0.01, 0.85), 2)
        
        data.append({
            "instance": host,
            "cpu_util_pct": cpu,
            "power_draw_watts": power,
            "ram_util_gb": ram_gb,
            "ram_total_gb": 128,
            "drive_fail_prob": drive_fail,
            "timestamp": datetime.now().isoformat(),
            "workload_class": random.choice(["batch-ml", "web-app", "database", "inference"])
        })
    return data

def mock_tnb_api() -> float:
    """
    Simulates the Tenaga Nasional Berhad (TNB) grid carbon intensity API.
    Malaysian grid intensity typically ranges between 0.5 and 0.7 kg CO2/kWh.

    Returns:
        float: Current grid carbon intensity in kg CO2e per kWh.
    """
    # Simulate slight hourly variation
    hour = datetime.now().hour
    base = 0.58
    variation = 0.02 * (hour / 12)  # Slightly higher during peak day hours
    return round(base + variation + random.uniform(-0.02, 0.02), 3)

def mock_github_pr(repo: str, branch: str, content: str, commit_msg: str) -> str:
    """
    Simulates a GitHub Pull Request creation for GitOps.

    Args:
        repo: Repository name.
        branch: Branch name for the changes.
        content: YAML/JSON patch content (ignored in mock).
        commit_msg: Commit message.

    Returns:
        str: Mock PR URL.
    """
    pr_number = random.randint(100, 999)
    return f"https://github.com/{repo}/pull/{pr_number}"

def mock_erp_requisition(sku: str, quantity: int, just: str) -> str:
    """
    Simulates an ERP purchase requisition (e.g., SAP/Oracle) for hardware refresh.

    Args:
        sku: Stock Keeping Unit (e.g., "Dell_R760").
        quantity: Number of units to order.
        just: Justification text (e.g., crossover date reached).

    Returns:
        str: Mock requisition ID.
    """
    return f"REQ-{datetime.now().strftime('%Y%m%d')}-{random.randint(1000, 9999)}"

# -------------------- REAL API WRAPPERS (Production Ready) --------------------
# Uncomment these and replace with actual API calls when moving to production.

"""
import httpx
from tenacity import retry, stop_after_attempt, wait_exponential

class PrometheusClient:
    def __init__(self, url: str, timeout: int = 10):
        self.url = url
        self.timeout = timeout

    @retry(stop=stop_after_attempt(3), wait=wait_exponential(multiplier=1, min=2, max=10))
    def query(self, query: str) -> Dict:
        response = httpx.get(
            f"{self.url}/api/v1/query",
            params={"query": query},
            timeout=self.timeout
        )
        response.raise_for_status()
        return response.json()

class TNBClient:
    def __init__(self, api_key: str):
        self.api_key = api_key
        self.endpoint = "https://api.tnb.com.my/grid/carbon"

    def get_current_co2(self) -> float:
        # Real implementation would authenticate and fetch live data
        pass
"""