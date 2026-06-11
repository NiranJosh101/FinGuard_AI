from src.config import settings

class LimitEvaluator:
    """
    Evaluates financial boundaries and absolute compliance caps 
    independent of specific user risk baselines.
    """

    def evaluate(self, amount: float) -> tuple[bool, list[str], list[str]]:
        """
        Evaluates transaction totals against global systemic safety ceilings.
        
        Args:
            amount (float): The scalar fiat value extracted from the user intent
            
        Returns:
            tuple: (is_violation: bool, triggered_rules: list, user_reasons: list)
        """
        triggered_rules = []
        user_facing_reasons = []

        # Validate against the absolute hard compliance maximum
        if amount > settings.MAX_TRANSACTION_CEILING_NGN:
            triggered_rules.append("RULE_LIMIT_EXCEEDED")
            user_facing_reasons.append(settings.MSG_LIMIT_EXCEEDED)

        is_violation = len(triggered_rules) > 0
        return is_violation, triggered_rules, user_facing_reasons