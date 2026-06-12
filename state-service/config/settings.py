import os

# Server Configurations
GRPC_PORT = int(os.getenv("GRPC_PORT", "50051"))

# Redis Engine Configurations
REDIS_HOST = os.getenv("REDIS_HOST", "localhost")
REDIS_PORT = int(os.getenv("REDIS_PORT", "6379"))
REDIS_PASSWORD = os.getenv("REDIS_PASSWORD", None)
REDIS_DB = int(os.getenv("REDIS_DB", "0"))

# Lifecycle Guardrails
DEFAULT_TTL_SECONDS = int(os.getenv("DEFAULT_TTL_SECONDS", "300"))  # 5-minute freeze limit