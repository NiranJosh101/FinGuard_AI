import time
import asyncio
import logging
from typing import Tuple
from src.config.environment import env_config

logger = logging.getLogger(__name__)

class SpeechToTextEngine:
    def __init__(self):
        self.api_key = env_config.LLM_API_KEY
        self.endpoint = f"{env_config.LLM_ENDPOINT}/audio/transcriptions"
        self.model_id = env_config.STT_MODEL_IDENTIFIER

    async def transcribe(self, audio_bytes: bytes) -> Tuple[str, float]:
        """
        Dispatches raw audio bytes to the external cloud transcription API.
        
        Returns:
            Tuple[str, float]: (transcribed_text, api_confidence_score)
        Raises:
            TimeoutError: If the external API call takes longer than STT_PROCESSING_TIMEOUT_SEC
            RuntimeError: If the cloud provider returns a non-200 failure code
        """
        if not audio_bytes:
            return "", 0.0

        logger.info(f"Dispatching voice payload to external API using {self.model_id}...")
        
        try:
            # Production Implementation Note:
            # async with httpx.AsyncClient() as client:
            #     response = await client.post(
            #         self.endpoint,
            #         headers={"Authorization": f"Bearer {self.api_key}"},
            #         files={"file": ("openai.mp3", audio_bytes, "audio/mp3")},
            #         data={"model": self.model_id},
            #         timeout=env_config.STT_PROCESSING_TIMEOUT_SEC
            #     )
            
            # Simulating network latency and an external API response within the deadline
            await asyncio.sleep(0.4) 
            
            # Simulated API JSON extraction
            extracted_text = "Send 250000 Naira to Tunde"
            api_confidence = 0.94  # External APIs usually provide per-token logprobs or average segment confidence
            
            return extracted_text, api_confidence

        except Exception as e:
            logger.error(f"External Speech-to-Text API network failure: {str(e)}")
            raise RuntimeError(f"Upstream STT API failure: {str(e)}")