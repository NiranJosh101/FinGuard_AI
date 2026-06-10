import os
import logging
from langchain_groq import ChatGroq
from dotenv import load_dotenv
from src.config.environment import env_config
from src.prompts.intent_prompts import INTENT_EXTRACTION_PROMPT

from src.schemas.intent_schema import IntentPayloadSchema
from generated.intent_pb2 import IntentPayload

load_dotenv()

logger = logging.getLogger(__name__)

class StructuredLLMEngine:
    def __init__(self, model_name: str = None):
        self.model_name = model_name or env_config.INTENT_LLM_MODEL
        
        self.llm = ChatGroq(
            temperature=0,
            model_name=self.model_name,
            groq_api_key=os.getenv("GROQ_API_KEY")
        )
        
        # Use Pydantic schema for LangChain — NOT the protobuf class
        self.structured_llm = self.llm.with_structured_output(IntentPayloadSchema)

    async def generate_structured_intent(self, sanitized_text: str) -> IntentPayload:
        """
        Synthesizes raw user inputs into a strongly typed, validated IntentPayload proto instance.
        """
        if not sanitized_text:
            raise ValueError("Sanitized text parameter cannot be empty or null.")

        formatted_prompt = INTENT_EXTRACTION_PROMPT.format(user_context=sanitized_text)
        
        logger.info(f"Invoking structured inference via {self.model_name} (Enforcing Schema)...")
        
        try:
            # ainvoke is the async-native path — no executor needed
            pydantic_result: IntentPayloadSchema = await self.structured_llm.ainvoke(formatted_prompt)
            
            # Convert Pydantic → Protobuf at the boundary before returning
            return pydantic_result.to_proto()
            
        except Exception as e:
            logger.error(f"Structured Extraction Engine Fault: {str(e)}")
            raise