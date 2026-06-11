from dataclasses import dataclass

@dataclass
class RiskResult:
    risk_level: str               # "LOW", "MEDIUM", "HIGH", "CRITICAL"
    risk_score: float             # 0.0 to 1.0
    recipient_is_new: bool
    velocity_limit_triggered: bool
    pattern_anomaly_detected: bool
    risk_evaluation_summary: str