import os

# Server Configurations
GRPC_PORT = os.getenv("GRPC_PORT", "50051")
MOCK_PROFILE_PATH = os.getenv(
    "MOCK_PROFILE_PATH", 
    os.path.join(os.path.dirname(__file__), "..", "profiles", "mock_user_profile.json")
)

# Risk Weight Allocations (Must equal 1.0 when combined maximum)
NEW_RECIPIENT_WEIGHT = 0.4
AMOUNT_ANOMALY_WEIGHT = 0.3
UNUSUAL_BEHAVIOR_WEIGHT = 0.3

# Evaluation Threshold Rules
AMOUNT_ANOMALY_MULTIPLIER = 3.0  # Trigger if amount > avg_amount * 3

# Risk Level Classification Thresholds
SCORE_THRESHOLD_LOW = 0.4    # < 0.4 is LOW
SCORE_THRESHOLD_MEDIUM = 0.8 # < 0.8 is MEDIUM, >= 0.8 is HIGH