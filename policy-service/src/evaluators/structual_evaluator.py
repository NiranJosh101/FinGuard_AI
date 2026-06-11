from src.config import settings

class StructuralEvaluator:
    """
    Evaluates the clarity, structural integrity, and validity of parsed user intents.
    Catches prompt injections, absolute gibberish, or missing parameter values.
    """

    def evaluate(self, action_type: int, is_ambiguous: bool) -> tuple[bool, list[str], list[str]]:
        """
        Runs structural sanity checks on the intent payload data.
        
        Args:
            action_type (int): Enum index value mapped from IntentPayload (0 = UNKNOWN_ACTION)
            is_ambiguous (bool): Explicit ambiguity flag set by the upstream intent LLM
            
        Returns:
            tuple: (is_violation: bool, triggered_rules: list, user_reasons: list)
        """
        triggered_rules = []
        user_facing_reasons = []

        # Check for Total Comprehension Failure / UNKNOWN_ACTION (Assuming enum 0 is unspecified/unknown)
        if action_type == 0:
            triggered_rules.append("RULE_UNKNOWN_ACTION")
            user_facing_reasons.append(settings.MSG_UNKNOWN_ACTION)

        # Check for Explicit Linguistic Ambiguity (e.g., "Send money to Tunde" with no amount)
        if is_ambiguous:
            triggered_rules.append("RULE_AMBIGUOUS_INTENT")
            user_facing_reasons.append(settings.MSG_AMBIGUOUS_INTENT)

        is_violation = len(triggered_rules) > 0
        return is_violation, triggered_rules, user_facing_reasons