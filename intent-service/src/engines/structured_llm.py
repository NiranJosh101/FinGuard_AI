import os
import logging
from langchain_groq import ChatGroq
from src.config.environment import env_config
from src.prompts.intent_prompts import INTENT_EXTRACTION_PROMPT

# Import the generated protobuf structural reference
from generated.intent_pb2 import IntentPayload

logger = logging.getLogger(__name__)

class StructuredLLMEngine:
    def __init__(self, model_name: str = None):
        # Fall back to environment configuration properties if not explicitly overridden
        self.model_name = model_name or env_config.INTENT_LLM_MODEL
        
        # We enforce temperature 0 for extraction to ensure deterministic financial outputs
        self.llm = ChatGroq(
            temperature=0,
            model_name=self.model_name,
            groq_api_key=env_config.LLM_API_KEY
        )
        
        # The LangChain "Magic" — it forces the LLM to return data conforming to the IntentPayload schema
        # Note: In production with LangChain, you can pass a Pydantic version of your proto definition here
        self.structured_llm = self.llm.with_structured_output(IntentPayload)

    async def generate_structured_intent(self, sanitized_text: str) -> IntentPayload:
        """
        Synthesizes raw user inputs into a strongly typed, validated IntentPayload schema instance.
        """
        if not sanitized_text:
            raise ValueError("Sanitized text parameter cannot be empty or null.")

        # 1. Format the isolated system prompt with the processed context text
        formatted_prompt = INTENT_EXTRACTION_PROMPT.format(user_context=sanitized_text)
        
        logger.info(f"Invoking structured inference via {self.model_name} (Enforcing Schema)...")
        
        # 2. Invoke the external cloud API structure
        try:
            # LangChain's invoke is typically synchronous for basic providers, wrap in executor or use ainvoke if supported
            intent_profile = self.structured_llm.invoke(formatted_prompt)
            return intent_profile
            
        except Exception as e:
            logger.error(f"Structured Extraction Engine Fault: {str(e)}")
            print(f"Extraction Error: {e}")
            raise e