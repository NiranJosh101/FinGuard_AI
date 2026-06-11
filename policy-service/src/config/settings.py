import os
from typing import Set
from pydantic_settings import BaseSettings, SettingsConfigDict


class PolicySettings(BaseSettings):
    """
    Defines the system-wide thresholds, rules, and limits for the Policy Engine.
    Values can be overridden using environment variables (e.g., POLICY_MAX_CEILING_NGN).
    """

    # --- Structural Defaults ---
    SYSTEM_NAME: str = "finguard-policy-service"
    ENV: str = "production"

    # --- Financial Ceilings ---
    # Absolute transaction ceiling (e.g., ₦1,000,000)
    MAX_CEILING_NGN: float = 1000000.0

    # --- Risk Threshold Steps ---
    # Any score equal to or higher than this triggers a hard BLOCK (unless overridden by track)
    # Applied to specific risky actions or combined score configurations
    RISK_SCORE_CRITICAL: float = 0.95
    
    # Risk Score >= 0.8 -> REQUIRE_APPROVAL (High Risk)
    RISK_THRESHOLD_APPROVAL: float = 0.8
    
    # Risk Score >= 0.4 AND < 0.8 -> REQUIRE_CONFIRMATION (Medium Risk)
    RISK_THRESHOLD_CONFIRMATION: float = 0.4

    # --- Operational Timeouts ---
    # Default TTL (Seconds) for step-up actions (e.g., 5 minutes)
    DEFAULT_CHALLENGE_TTL_SECONDS: int = 300

    # --- Rule Error/Reason Messages ---
    MSG_AMBIGUOUS_INTENT: str = "Transaction parameters are ambiguous or incomplete."
    MSG_UNKNOWN_ACTION: str = "Unrecognized transaction or system instruction requested."
    MSG_LIMIT_EXCEEDED: str = "Transaction violates single-operation limit ceiling."
    MSG_NEW_RECIPIENT: str = "New recipient detected. Additional verification required."
    MSG_HIGH_RISK_SCORE: str = "Elevated transactional anomalies flagged by security telemetry."
    MSG_SAFE_TRANSACTION: str = "Transaction successfully verified within baseline parameters."

    # Allow configuration loading from environment variables or .env files
    model_config = SettingsConfigDict(
        env_prefix="POLICY_",
        case_sensitive=True,
        env_file=".env",
        env_file_encoding="utf-8",
        extra="ignore"
    )


# Globally accessible configuration instance
settings = PolicySettings()