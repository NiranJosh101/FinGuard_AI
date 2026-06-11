from src.config import settings
from src.evaluators.structual_evaluator import StructuralEvaluator
from src.evaluators.limit_evaluator import LimitEvaluator
from src.evaluators.risk_mapper import RiskMapper
from generated.policy_pb2 import BLOCK, PolicyDecision

class PolicyEngine:
    """
    The main coordinator for the Policy Enforcement Engine.
    Executes a cascaded, zero-trust evaluation chain across structural, 
    financial, and security rules to output a definitive system directive.
    """

    def __init__(self):
        # Initialize internal evaluation units
        self.structural_evaluator = StructuralEvaluator()
        self.limit_evaluator = LimitEvaluator()
        self.risk_mapper = RiskMapper()

    def evaluate_policy(
        self, 
        action_type: int, 
        is_ambiguous: bool, 
        amount: float, 
        risk_score: float, 
        recipient_is_new: bool
    ) -> PolicyDecision:
        """
        Processes an incoming intent and risk profile through sequential policy tracks.
        
        Args:
            action_type (int): Enum index value representing user intent
            is_ambiguous (bool): Explicit ambiguity validation flag from the LLM
            amount (float): Raw currency value requested
            risk_score (float): Security score baseline from the Risk Engine
            recipient_is_new (bool): Target account velocity flag
            
        Returns:
            PolicyDecision: The final populated Protobuf payload message
        """
        
        # --- TRACK 1: Structural Integrity (Priority 1 Hard Guardrail) ---
        struct_violation, struct_rules, struct_reasons = self.structural_evaluator.evaluate(
            action_type=action_type, 
            is_ambiguous=is_ambiguous
        )
        if struct_violation:
            return PolicyDecision(
                effect=BLOCK,
                triggered_rules=struct_rules,
                user_facing_reasons=struct_reasons,
                challenge_ttl_seconds=0  # Blocks have zero lifespan validity
            )

        # --- TRACK 2: Compliance Ceiling Limits (Priority 2 Hard Guardrail) ---
        limit_violation, limit_rules, limit_reasons = self.limit_evaluator.evaluate(
            amount=amount
        )
        if limit_violation:
            return PolicyDecision(
                effect=BLOCK,
                triggered_rules=limit_rules,
                user_facing_reasons=limit_reasons,
                challenge_ttl_seconds=0
            )

        # --- TRACK 3: Risk Mapping & Friction Windows (Priority 3, 4, 5 Soft Guardrails) ---
        effect, risk_rules, risk_reasons = self.risk_mapper.map_to_effect(
            risk_score=risk_score, 
            recipient_is_new=recipient_is_new
        )

        # Determine TTL for holding parameters based on the friction required
        # If the transaction is outright ALLOWED, no hold token/TTL is needed (0)
        ttl = settings.CHALLENGE_TTL_SECONDS if effect in (2, 3) else 0

        return PolicyDecision(
            effect=effect,
            triggered_rules=risk_rules,
            user_facing_reasons=risk_reasons,
            challenge_ttl_seconds=ttl
        )