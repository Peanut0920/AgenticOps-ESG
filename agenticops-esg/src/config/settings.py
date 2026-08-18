"""
Application settings using Pydantic Settings.
Reads from .env file and environment variables.
"""

from typing import Optional
from pydantic_settings import BaseSettings

class AppSettings(BaseSettings):
    """
    Main application settings container.
    All fields are automatically populated from .env or system environment variables.
    """

    # --- Environment & Runtime ---
    environment: str = "development"
    session_prefix: str = "agenticops-v1"
    log_level: str = "INFO"
    
    # --- External APIs (Prometheus / TNB) ---
    prometheus_url: str = "http://localhost:9090"
    tnb_api_key: Optional[str] = None  # Mock fallback if not provided
    
    # --- GitOps & ERP ---
    github_token: Optional[str] = None
    gitops_repo: str = "infra-as-code"
    
    # --- Regulatory Portals (for auto-submission) ---
    bursa_api_endpoint: str = "https://api.bursamalaysia.com/v2/sustainability"
    mcmc_api_endpoint: str = "https://api.mcmc.gov.my/technical-code"
    
    # --- Feature Flags ---
    enable_auto_approve: bool = False  # If True, bypasses human-in-the-loop
    enable_mock_mode: bool = True     # If True, uses mock APIs instead of real ones

    class Config:
        env_file = ".env"
        env_file_encoding = "utf-8"
        case_sensitive = False

# Singleton instance for easy import across the application
settings = AppSettings()