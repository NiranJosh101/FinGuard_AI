import os

# Server Configurations
GRPC_PORT = os.getenv("GRPC_PORT", "50052")  # Using 50052 to separate from Risk Service (50051)

# Hard Compliance Ceilings
MAX_TRANSACTION_CEILING_NGN = float(os.getenv("MAX_TRANSACTION_CEILING_NGN", "1000000.0"))

# Policy Risk Step Thresholds (Decision Matrix Steps)
RISK_THRESHOLD_CONFIRMATION = float(os.getenv("RISK_THRESHOLD_CONFIRMATION", "0.4")) # >= 0.4 is Medium Risk
RISK_THRESHOLD_APPROVAL = float(os.getenv("RISK_THRESHOLD_APPROVAL", "0.8"))         # >= 0.8 is High Risk

# Operational Token Lifespan
CHALLENGE_TTL_SECONDS = int(os.getenv("CHALLENGE_TTL_SECONDS", "300")) # 5-minute hold windows

# User-Facing Intent Explanations
MSG_AMBIGUOUS_INTENT = "Transaction parameters are ambiguous or incomplete."
MSG_UNKNOWN_ACTION = "Unrecognized transaction or system instruction requested."
MSG_LIMIT_EXCEEDED = f"Transaction violates single-operation limit ceiling of ₦{MAX_TRANSACTION_CEILING_NGN:,.2f}."
MSG_NEW_RECIPIENT = "New recipient detected. Additional verification required."
MSG_HIGH_RISK_SCORE = "Elevated transactional anomalies flagged by security telemetry."
MSG_SAFE_TRANSACTION = "Transaction successfully verified within baseline parameters."