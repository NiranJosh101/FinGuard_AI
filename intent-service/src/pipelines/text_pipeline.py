import logging
from src.pipelines.base_pipeline import BasePipeline

logger = logging.getLogger(__name__)

class TextPipeline(BasePipeline):
    def __init__(self):
        # Enforce the strict 500 character system ceiling for conversational text
        super().__init__(max_characters=500)

    async def process(self, payload) -> str:
        """
        Ingests the incoming text payload from the ingress wire contract,
        verifies its integrity, and runs it through the base security sanitizer.
        
        Returns:
            str: Normalized, sanitized textual instruction.
        Raises:
            ValueError: For explicit prompt injection strings or malformed fields.
        """
        # 1. Soft Guardrail: Fallback if text field is missing or empty
        if not hasattr(payload, 'text_content') or not payload.text_content:
            logger.warning("Text pipeline received an empty or missing text payload string.")
            return "UNKNOWN_ACTION"

        # 2. Extract and run structural formatting adjustments
        raw_text = payload.text_content.strip()

        # 3. Security Hard Guardrail: Put the untrusted text straight through the firewall
        try:
            logger.info("Routing inbound string down the direct sanitization filter track...")
            sanitized_text = self.sanitize_text(raw_text)
            
            # If the user string was completely stripped or minimized to nothing, flag it
            if not sanitized_text:
                return "UNKNOWN_ACTION"
                
            return sanitized_text

        except ValueError as security_err:
            # Absolute stop: Log critical threat vector information for auditing
            logger.critical(f"Inbound Text Security Threat Deflected: {str(security_err)}")
            raise ValueError(f"Payload Rejected: {str(security_err)}")