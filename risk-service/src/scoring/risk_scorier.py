from src.config import settings
from typing import Tuple

def calculate_score(
    recipient_is_new: bool,
    pattern_anomaly_detected: bool,
    velocity_limit_triggered: bool
) -> Tuple[float, str]:
    """
    Calculates a risk score scaled between 0.0 and 1.0 based on tripped risk signals.
    Maps the final mathematical score back to a readable risk string framework.
    """
    score = 0.0

    # Apply Weights configured in settings
    if recipient_is_new:
        score += settings.NEW_RECIPIENT_WEIGHT
        
    if pattern_anomaly_detected:
        score += settings.AMOUNT_ANOMALY_WEIGHT
        
    if velocity_limit_triggered:
        score += settings.UNUSUAL_BEHAVIOR_WEIGHT  # Reuse behavior/velocity weight allocation

    # Clamp upper boundary securely at 1.0
    score = min(score, 1.0)
    
    # Map to String Categories matching our Proto enum ranges
    if score < settings.SCORE_THRESHOLD_LOW:
        level = "LOW"
    elif score < settings.SCORE_THRESHOLD_MEDIUM:
        level = "MEDIUM"
    elif score == 1.0:
        level = "CRITICAL"
    else:
        level = "HIGH"

    return round(score, 2), level