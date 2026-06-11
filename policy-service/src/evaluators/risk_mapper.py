from src.config import settings
from generated.policy_pb2 import (
    ALLOW,
    REQUIRE_CONFIRMATION,
    REQUIRE_APPROVAL,
    PolicyEffect
)

class RiskMapper:
    """
    Transforms continuous risk telemetry variables into discrete,
    actionable transactional policy tracks based on strict compliance thresholds.
    """

    def map_to_effect(self, risk_score: float, recipient_is_new: bool) -> tuple[PolicyEffect, list[str], list[str]]:
        """
        Maps telemetry dimensions onto the operational policy branch matrix.
        
        Args:
            risk_score (float): Calculated telemetry float score from Risk Engine
            recipient_is_new (bool): Velocity/directory resolution tracking flag
            
        Returns:
            tuple: (effect: PolicyEffect enum, triggered_rules: list, user_reasons: list)
        """
        triggered_rules = []
        user_facing_reasons = []

        # Branch B: REQUIRE_APPROVAL (High Risk Track)
        # Triggered by a new recipient directory entry OR an elevated risk score >= 0.8
        if recipient_is_new or risk_score >= settings.RISK_THRESHOLD_APPROVAL:
            effect = REQUIRE_APPROVAL
            
            if recipient_is_new:
                triggered_rules.append("RULE_NEW_RECIPIENT")
                user_facing_reasons.append(settings.MSG_NEW_RECIPIENT)
            if risk_score >= settings.RISK_THRESHOLD_APPROVAL:
                triggered_rules.append("RULE_HIGH_RISK_SCORE")
                user_facing_reasons.append(settings.MSG_HIGH_RISK_SCORE)
                
            return effect, triggered_rules, user_facing_reasons

        # Branch C: REQUIRE_CONFIRMATION (Medium Risk Track)
        # Triggered by a moderate deviation score: 0.4 <= risk_score < 0.8
        elif risk_score >= settings.RISK_THRESHOLD_CONFIRMATION:
            effect = REQUIRE_CONFIRMATION
            triggered_rules.append("RULE_ELEVATED_RISK")
            user_facing_reasons.append(settings.MSG_HIGH_RISK_SCORE)
            return effect, triggered_rules, user_facing_reasons

        # Branch D: ALLOW (The Fast Track)
        # Low risk anomalies that clear baseline metrics: risk_score < 0.4
        else:
            effect = ALLOW
            triggered_rules.append("RULE_SAFE_BASELINE")
            user_facing_reasons.append(settings.MSG_SAFE_TRANSACTION)
            return effect, triggered_rules, user_facing_reasons