import logging
import grpc
from generated import policy_pb2_grpc
from generated.policy_pb2 import PolicyDecision
from src.services.policy_engine import PolicyEngine

# Setup telemetry logging for enforcement auditing
logger = logging.getLogger("finguard.policy_service")

class PolicyServicer(policy_pb2_grpc.PolicyServiceServicer):
    """
    gRPC network interface handling incoming payload parameters, unpacking
    serialized stream fields, and executing the central policy decision tree.
    """

    def __init__(self):
        # Instantiate our atomic service engine coordinator
        self.engine = PolicyEngine()

    def EvaluateTransactionPolicy(self, request, context):
        """
        RPC endpoint handler that receives metadata and returns the final system directive.
        
        Args:
            request: The incoming gRPC request containing intent and risk contexts
            context: gRPC network request thread context
            
        Returns:
            PolicyDecision: The populated proto response tracking safety constraints
        """
        try:
            # Safely unpack primitives from the incoming transport payload
            intent = request.intent_payload
            risk = request.risk_profile

            logger.info(
                f"Evaluating Policy | Action: {intent.action_type} | "
                f"Amount: ₦{intent.amount:,.2f} | Risk Score: {risk.risk_score}"
            )

            # Route primitives straight into our deterministic logical core
            decision = self.engine.evaluate_policy(
                action_type=intent.action_type,
                is_ambiguous=intent.is_ambiguous,
                amount=intent.amount,
                risk_score=risk.risk_score,
                recipient_is_new=risk.recipient_is_new
            )

            logger.info(f"Policy Decision Concluded | Effect Selected: {decision.effect}")
            return decision

        except AttributeError as err:
            # Catch anomalies resulting from missing or misconfigured contract schemas
            logger.error(f"Malformed structural payload signature received: {str(err)}")
            context.set_code(grpc.StatusCode.INVALID_ARGUMENT)
            context.set_details("Payload missing required 'intent_payload' or 'risk_profile' configurations.")
            return PolicyDecision()
            
        except Exception as e:
            # Catch-all safety net for system runtime operations
            logger.critical(f"Unhandled exception during policy evaluation lifecycle: {str(e)}")
            context.set_code(grpc.StatusCode.INTERNAL)
            context.set_details("Internal runtime exception encountered inside Policy Service.")
            return PolicyDecision()