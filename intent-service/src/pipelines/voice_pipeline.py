import asyncio
import logging
from typing import Tuple
from src.pipelines.base_pipeline import BasePipeline
from src.engines.speech_to_text import SpeechToTextEngine
from src.config.environment import env_config

logger = logging.getLogger(__name__)

class VoicePipeline(BasePipeline):
    def __init__(self, stt_engine: SpeechToTextEngine = None):
        # Enforce the system default character limit on the base pipeline
        super().__init__(max_characters=500)
        self.stt_engine = stt_engine or SpeechToTextEngine()
        # Define a baseline threshold for speech recognition confidence
        self.min_confidence_threshold = 0.50

    async def process(self, payload) -> str:
        """
        Ingests the ingress payload, extracts the audio binary track, 
        transcribes it with defensive timeouts, and runs post-transcription
        soft guardrails.
        
        Returns:
            str: Cleaned and sanitized text transcript.
        Raises:
            ValueError: For security violations or catastrophic payload failures.
        """
        # 1. Soft Guardrail: Check if audio bytes exist
        if not hasattr(payload, 'audio_bytes') or not payload.audio_bytes:
            logger.warning("Voice pipeline received an empty or missing audio byte payload.")
            return "UNKNOWN_ACTION"

        try:
            # 2. Hard Guardrail: Enforce the strict operational system timeout
            logger.info("Initiating transcription with strict timeout guardrail...")
            
            transcribed_text, api_confidence = await asyncio.wait_for(
                self.stt_engine.transcribe(payload.audio_bytes),
                timeout=env_config.STT_PROCESSING_TIMEOUT_SEC
            )

        except asyncio.TimeoutError:
            # Hard Guardrail triggered: Downstream node took too long
            logger.error(f"Voice pipeline aborted: Transcription exceeded {env_config.STT_PROCESSING_TIMEOUT_SEC}s threshold.")
            return "UNKNOWN_ACTION"
            
        except Exception as e:
            # Catch engine or upstream cloud provider failures gracefully
            logger.error(f"Voice pipeline failed due to underlying engine error: {str(e)}")
            return "UNKNOWN_ACTION"

        # 3. Soft Guardrail: Handle silent or unintelligible audio files
        if not transcribed_text.strip():
            logger.warning("Speech-to-text returned an empty string. Audio may be silent or entirely noise.")
            return "UNKNOWN_ACTION"

        # 4. Soft Guardrail: Handle low confidence scores
        if api_confidence < self.min_confidence_threshold:
            logger.warning(
                f"Transcription confidence ({api_confidence}) dropped below system threshold ({self.min_confidence_threshold})."
            )
            return "UNKNOWN_ACTION"

        # 5. Security Guardrail: Run the extracted text through the Base Class Sanitizer
        # This catches prompt injection attacks hidden inside voice data ("voice squatting")
        try:
            sanitized_text = self.sanitize_text(transcribed_text)
            return sanitized_text
        except ValueError as security_err:
            logger.critical(f"Inbound Voice Security Violation Caught: {str(security_err)}")
            raise ValueError(f"Payload Rejected: {str(security_err)}")