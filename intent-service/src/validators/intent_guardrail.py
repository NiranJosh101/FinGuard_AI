import logging
from src.config.environment import env_config
from generated.intent_pb2 import IntentPayload, ActionType, TargetNetwork

logger = logging.getLogger(__name__)

class IntentGuardrail:
    def __init__(self):
        # System maximum ceiling configuration parsed as float/double baseline value (e.g., 1000000.00 NGN)
        self.max_ceiling = float(env_config.SYSTEM_MAX_CEILING) 

    def validate_and_gate(self, intent_payload: IntentPayload) -> tuple:
        """
        Performs non-AI, strict verification loops adhering exclusively to the 
        finguard.intent protobuf fields schema layout.
        """
        logger.info("Evaluating intent output fields under strict defined schema rules...")

        # 1. HARD GUARDRAIL: Absolute Monetary Ceiling Enforcement
        if intent_payload.amount > self.max_ceiling:
            logger.critical(
                f"HARD BLOCK: Transaction amount {intent_payload.amount} "
                f"violates system ceiling boundary of {self.max_ceiling}."
            )
            intent_payload.is_ambiguous = False
            intent_payload.status_message = "Transaction rejected: Exceeds the maximum allowable transfer ceiling."
            return intent_payload, "BLOCK"

        # 2. SOFT GUARDRAIL: Cross-Field Ambiguity Remediation Analysis
        # Check if the intent implies money moving (TRANSFER or BUY_CRYPTO)
        if intent_payload.action in [ActionType.TRANSFER, ActionType.BUY_CRYPTO]:
            
            # Case A: Amount missing or invalid
            if intent_payload.amount <= 0.0:
                logger.warning("SOFT GUARDRAIL: Financial routing action flagged without a specified amount.")
                intent_payload.is_ambiguous = True
                intent_payload.status_message = "Please specify the exact amount of money you would like to transact."
                return intent_payload, "REMEDIATE"
                
            # Case B: Routing target validation checks
            if intent_payload.action == ActionType.TRANSFER and intent_payload.target_network == TargetNetwork.CRYPTO_BLOCKCHAIN:
                logger.warning("SOFT GUARDRAIL: Contradictory action path. Standard transfer mapped to blockchain ledger.")
                intent_payload.is_ambiguous = True
                intent_payload.status_message = "Your request mentions a bank transfer but points to a blockchain asset. Please clarify."
                return intent_payload, "REMEDIATE"

            # Case C: Identity validation checks
            if not intent_payload.recipient_alias.strip():
                logger.warning("SOFT GUARDRAIL: Destination alias parameter is completely blank.")
                intent_payload.is_ambiguous = True
                intent_payload.status_message = "Who is the intended recipient for this transaction? Please specify an alias."
                return intent_payload, "REMEDIATE"

        # 3. HAPPY PATH: System clearance verification
        logger.info("Programmatic guardrail verification successfully finalized.")
        return intent_payload, "PROCEED"