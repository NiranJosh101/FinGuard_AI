import logging
from src.pipelines.text_pipeline import TextPipeline
from src.pipelines.voice_pipeline import VoicePipeline
from src.pipelines.image_pipeline import ImagePipeline
from src.engines.structured_llm import StructuredLLMEngine
from src.validators.intent_guardrail import IntentGuardrail

# Assuming these are generated structures matching your intent_pb2 layout
from generated.intent_pb2 import IntentPayload 

logger = logging.getLogger(__name__)

class MasterOrchestrator:
    def __init__(
        self,
        text_pipeline: TextPipeline = None,
        voice_pipeline: VoicePipeline = None,
        image_pipeline: ImagePipeline = None,
        llm_engine: StructuredLLMEngine = None,
        guardrail: IntentGuardrail = None
    ):
        # Inject dependencies or instantiate defaults
        self.text_pipeline = text_pipeline or TextPipeline()
        self.voice_pipeline = voice_pipeline or VoicePipeline()
        self.image_pipeline = image_pipeline or ImagePipeline()
        self.llm_engine = llm_engine or StructuredLLMEngine()
        self.guardrail = guardrail or IntentGuardrail()

    async def route_and_execute(self, ingress_payload) -> tuple:
        """
        Intercepts incoming wire-contract payloads, routes them to the correct 
        media processor, infers structural semantic intent, and runs final defensive checks.
        
        Args:
            ingress_payload: The raw compiled generated/ingress_pb2 instance.
            
        Returns:
            tuple: (IntentPayload, action_status)
        """
        # Determine track based on the wire contract's input_type header (Enum or String)
        # Supporting both integer enums or string matching variants based on protobuf setups
        input_type = getattr(ingress_payload, "input_type", "").upper()
        
        logger.info(f"Master Switchboard tracking incoming packet payload type: {input_type}")
        context_string = "UNKNOWN_ACTION"

        # ---------------------------------------------------------------------
        # STEP 1: Route Payload to the Appropriate Intake Pipeline Track
        # ---------------------------------------------------------------------
        try:
            if input_type in ["TEXT", "1"]:
                context_string = await self.text_pipeline.process(ingress_payload)
                
            elif input_type in ["VOICE", "AUDIO", "2"]:
                context_string = await self.voice_pipeline.process(ingress_payload)
                
            elif input_type in ["IMAGE", "VISUAL", "3"]:
                context_string = await self.image_pipeline.process(ingress_payload)
                
            else:
                logger.error(f"Unrecognized service payload structure track: {input_type}")
                context_string = "UNKNOWN_ACTION"

        except ValueError as security_alert:
            # Short-circuit immediately if a pipeline raises a Prompt Injection exploit
            logger.critical(f"Orchestrator firewall halting execution: {str(security_alert)}")
            fallback_payload = IntentPayload(
                action_type="BLOCKED",
                is_ambiguous=False,
                boundary_message=f"Security Abort: {str(security_alert)}"
            )
            return fallback_payload, "BLOCK"

        # ---------------------------------------------------------------------
        # STEP 2: Handle Early Pipeline Failures (Silence, Empty Data, Missing Media)
        # ---------------------------------------------------------------------
        if context_string == "UNKNOWN_ACTION":
            logger.warning("Pipeline intake failed to resolve string context. Short-circuiting LLM node.")
            fallback_payload = IntentPayload(
                action_type="UNKNOWN",
                is_ambiguous=True,
                boundary_message="System was unable to read or parse your input instruction."
            )
            return fallback_payload, "REMEDIATE"

        # ---------------------------------------------------------------------
        # STEP 3: Dispatch Cleaned Context to the Inference Engine
        # ---------------------------------------------------------------------
        logger.info("Context clear. Querying LLM execution rails for structured layout...")
        try:
            # The structured engine compels the LLM to populate and return an IntentPayload
            raw_intent_output = await self.llm_engine.extract_intent(context_string)
        except Exception as inference_error:
            logger.error(f"Core inference node suffered execution runtime crash: {str(inference_error)}")
            fallback_payload = IntentPayload(
                action_type="SYSTEM_ERROR",
                is_ambiguous=False,
                boundary_message="Internal pipeline failure processing semantic structural models."
            )
            return fallback_payload, "BLOCK"

        # ---------------------------------------------------------------------
        # STEP 4: Submit Structured Output to Programmatic Gating Validators
        # ---------------------------------------------------------------------
        logger.info("Executing defensive post-inference constraints...")
        validated_payload, action_status = self.guardrail.validate_and_gate(raw_intent_output)

        return validated_payload, action_status