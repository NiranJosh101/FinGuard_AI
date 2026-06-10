import os
from dataclasses import dataclass, field

@dataclass(frozen=True)
class EnvironmentConfig:
    # --- System & Server Infrastructure ---
    ENV: str = field(default_factory=lambda: os.getenv("FIN_ENV", "development").lower())
    SERVER_PORT: int = field(default_factory=lambda: int(os.getenv("INTENT_SERVICE_PORT", "50051")))
    
    # --- Core LLM Engine Configuration ---
    LLM_API_KEY: str = field(default_factory=lambda: os.getenv("LLM_API_KEY", ""))
    LLM_ENDPOINT: str = field(default_factory=lambda: os.getenv("LLM_ENDPOINT", "https://api.openai.com/v1"))
    INTENT_LLM_MODEL: str = field(default_factory=lambda: os.getenv("INTENT_LLM_MODEL", "gpt-4o"))
    MIN_LLM_CONFIDENCE_THRESHOLD: float = field(default_factory=lambda: float(os.getenv("MIN_LLM_CONFIDENCE_THRESHOLD", "0.75")))
    
    # --- Voice Processing Vector (STT) ---
    WHISPER_ENGINE_TYPE: str = field(default_factory=lambda: os.getenv("WHISPER_ENGINE_TYPE", "local"))  # 'local' or 'api'
    STT_MODEL_IDENTIFIER: str = field(default_factory=lambda: os.getenv("STT_MODEL_IDENTIFIER", "whisper-base"))
    STT_CONFIDENCE_THRESHOLD: float = field(default_factory=lambda: float(os.getenv("STT_CONFIDENCE_THRESHOLD", "0.60")))
    
    # --- Image Processing Vector (Vision/OCR) ---
    VISION_ENGINE_TYPE: str = field(default_factory=lambda: os.getenv("VISION_ENGINE_TYPE", "local_ocr")) # 'local_ocr' or 'multimodal'
    VISION_MODEL_IDENTIFIER: str = field(default_factory=lambda: os.getenv("VISION_MODEL_IDENTIFIER", "tesseract"))

    # --- Hard System Compliance Ceilings ---
    # ₦1,000,000 ceiling mapped entirely in minor units (Kobo) to ensure deterministic integer math
    ABSOLUTE_SYSTEM_CEILING_MINOR_UNITS: int = field(default=100000000)

    # --- Latency & Execution Timeout Budgets (Seconds) ---
    TOTAL_ORCHESTRATOR_TIMEOUT_SEC: float = field(default_factory=lambda: float(os.getenv("TOTAL_ORCHESTRATOR_TIMEOUT_SEC", "4.0")))
    STT_PROCESSING_TIMEOUT_SEC: float = field(default_factory=lambda: float(os.getenv("STT_PROCESSING_TIMEOUT_SEC", "1.5")))
    VISION_PROCESSING_TIMEOUT_SEC: float = field(default_factory=lambda: float(os.getenv("VISION_PROCESSING_TIMEOUT_SEC", "2.0")))

    def validate(self) -> None:
        """
        Runs post-initialization assertion checks to prevent the service 
        from booting up with missing critical credentials in production.
        """
        if self.ENV in ("staging", "production"):
            assert self.LLM_API_KEY, f"CRITICAL: LLM_API_KEY must be set in {self.ENV} mode."
            if self.WHISPER_ENGINE_TYPE == "api" or self.VISION_ENGINE_TYPE == "multimodal":
                assert self.LLM_API_KEY, "CRITICAL: Remote AI APIs require a valid LLM_API_KEY token."


# Singleton instance initialization to be imported across the service modules
env_config = EnvironmentConfig()

# Fail-fast check on startup if config rules are broken
if __name__ == "__main__":
    try:
        env_config.validate()
        print(f"✅ Configuration loaded successfully in [{env_config.ENV}] mode on port {env_config.SERVER_PORT}.")
    except AssertionError as e:
        print(f"❌ Configuration Validation Failed: {e}")