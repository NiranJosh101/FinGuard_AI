import asyncio
import logging
from typing import Tuple
from src.pipelines.base_pipeline import BasePipeline
from src.engines.vision_ocr import VisionOCREngine
from src.config.environment import env_config

logger = logging.getLogger(__name__)

class ImagePipeline(BasePipeline):
    def __init__(self, vision_engine: VisionOCREngine = None):
        # Image text dumps can be long; we increase max_characters specifically 
        # for complex transaction structures while still preserving a bound.
        super().__init__(max_characters=1000)
        self.vision_engine = vision_engine or VisionOCREngine()
        # Define a high minimum threshold for financial OCR character reliability
        self.min_confidence_threshold = 0.65

    async def process(self, payload) -> str:
        """
        Ingests the ingress payload, extracts the image binary bytes, dispatches 
        them to the multimodal OCR cluster under strict timeout rules, and passes
        the output through defensive validation blocks.
        
        Returns:
            str: Normalized, sanitized textual context extracted from the image.
        Raises:
            ValueError: For security violations or catastrophic payload failures.
        """
        # 1. Soft Guardrail: Fallback immediately if image payload is empty
        if not hasattr(payload, 'image_bytes') or not payload.image_bytes:
            logger.warning("Image pipeline received an empty or missing image byte payload.")
            return "UNKNOWN_ACTION"

        try:
            # 2. Hard Guardrail: Enforce structural execution timeout rules
            logger.info("Initiating Vision OCR inference with strict timeout guardrail...")
            
            extracted_text, api_confidence = await asyncio.wait_for(
                self.vision_engine.extract_text(payload.image_bytes),
                timeout=env_config.VISION_PROCESSING_TIMEOUT_SEC
            )

        except asyncio.TimeoutError:
            # Hard Guardrail triggered: Processing oversized image took too long
            logger.error(f"Image pipeline aborted: OCR exceeded {env_config.VISION_PROCESSING_TIMEOUT_SEC}s threshold.")
            return "UNKNOWN_ACTION"
            
        except Exception as e:
            # Soft fallback: Catch cloud network drops or model crashes gracefully
            logger.error(f"Image pipeline failed due to underlying vision engine error: {str(e)}")
            return "UNKNOWN_ACTION"

        # 3. Soft Guardrail: Handle images with no readable text elements
        if not extracted_text.strip():
            logger.warning("Vision OCR returned an entirely blank or unreadable string.")
            return "UNKNOWN_ACTION"

        # 4. Soft Guardrail: Filter out heavily pixelated or low-confidence extractions
        if api_confidence < self.min_confidence_threshold:
            logger.warning(
                f"Vision confidence ({api_confidence}) dropped below system threshold ({self.min_confidence_threshold})."
            )
            return "UNKNOWN_ACTION"

        # 5. Security Hard Guardrail: Check text against prompt injection patterns.
        # This acts as an immediate firewall blocking visual text extraction attacks.
        try:
            sanitized_text = self.sanitize_text(extracted_text)
            return sanitized_text
        except ValueError as security_err:
            logger.critical(f"Inbound Visual Document Security Violation Caught: {str(security_err)}")
            raise ValueError(f"Payload Rejected: {str(security_err)}")