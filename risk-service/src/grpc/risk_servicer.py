import logging
import grpc
from generated import risk_pb2, risk_pb2_grpc
from src.services.risk_engine import RiskEngine

logger = logging.getLogger(__name__)

class RiskServicer(risk_pb2_grpc.RiskServiceServicer):
    
    def EvaluateRisk(self, request, context):
        """
        gRPC RPC implementation for handling IntentPayload evaluations.
        """
        logger.info(f"Received EvaluateRisk request for action: {request.action}")
        
        try:
            # 1. Delegate core business calculations to our domain service
            result = RiskEngine.evaluate(request)
            
            # 2. Map calculated string level status back to our strict gRPC proto Enums
            proto_risk_level = risk_pb2.RiskLevel.Value(result.risk_level)
            
            # 3. Construct and return response profile message
            return risk_pb2.RiskProfile(
                risk_level=proto_risk_level,
                risk_score=result.risk_score,
                recipient_is_new=result.recipient_is_new,
                velocity_limit_triggered=result.velocity_limit_triggered,
                pattern_anomaly_detected=result.pattern_anomaly_detected,
                risk_evaluation_summary=result.risk_evaluation_summary
            )
            
        except Exception as e:
            logger.exception("Internal error occurred during risk matrix scoring evaluation loop")
            context.set_code(grpc.StatusCode.INTERNAL)
            context.set_details(f"Internal evaluation engine failure: {str(e)}")
            return risk_pb2.RiskProfile()