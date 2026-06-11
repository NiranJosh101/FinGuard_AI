import logging
from src.profiles.profile_loader import load_profile
from src.evaluators.recipient_evaluator import is_new_recipient
from src.evaluators.amount_evaluator import is_amount_anomalous
from src.evaluators.bahavior_evaluator import is_behavior_unusual
from src.scoring.risk_scorier import calculate_score
from src.models.risk_result import RiskResult

logger = logging.getLogger(__name__)

class RiskEngine:
    @staticmethod
    def evaluate(intent) -> RiskResult:
        """
        Orchestrates full verification workflow mapping intent data to historical metrics.
        Accepts a gRPC IntentPayload duck-typed object.
        """
        # 1. Load mock data analytics record
        profile = load_profile()
        
        # Fallback values safely if empty profile dictionary encountered
        known_recipients = profile.get("known_recipients", [])
        avg_amount = profile.get("average_transfer_amount", 0.0)
        common_networks = profile.get("common_networks", [])
        common_categories = profile.get("common_categories", [])

        # 2. Execute rule evaluation flags
        recip_new = is_new_recipient(intent.recipient_alias, known_recipients)
        amount_anom = is_amount_anomalous(intent.amount, avg_amount)
        
        # Velocity limit simulated via behavioral pattern deviations 
        # (e.g. target rails or transactional types mismatch standard telemetry)
        velocity_triggered = is_behavior_unusual(
            intent.target_network, common_networks, 
            intent.category, common_categories
        )

        # 3. Calculate metrics aggregation
        risk_score, risk_level = calculate_score(recip_new, amount_anom, velocity_triggered)

        # 4. Generate dynamic textual audit logs
        summaries = []
        if recip_new:
            summaries.append("Recipient not found in known recipients historical index.")
        if amount_anom:
            summaries.append(f"Transfer amount spikes over threshold baseline limits (>3x of {avg_amount}).")
        if velocity_triggered:
            summaries.append("Structural rails behavioral mismatch or anomalous velocity markers detected.")
            
        summary_text = " ".join(summaries) if summaries else "Transaction matches expected historical consumer behavior benchmarks."

        logger.info(f"Risk evaluation finalized for intent: Score={risk_score} Level={risk_level}")

        return RiskResult(
            risk_level=risk_level,
            risk_score=risk_score,
            recipient_is_new=recip_new,
            velocity_limit_triggered=velocity_triggered,
            pattern_anomaly_detected=amount_anom,
            risk_evaluation_summary=summary_text
        )