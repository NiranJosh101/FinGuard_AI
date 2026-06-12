import asyncio
import logging
import grpc
from config import settings
from src.repository import TransactionRepository
from src.engine import StateEngine
from generated.state_service_pb2_grpc import (
    TransactionStateServiceServicer, 
    add_TransactionStateServiceServicer_to_server
)
from generated.state_service_pb2 import (
    FreezeResponse, 
    GetTransactionResponse, 
    MutateStatusResponse
)

# Configure structured logging
logging.basicConfig(
    level=logging.INFO,
    format="%(asctime)s [%(levelname)s] %(name)s: %(message)s"
)
logger = logging.getLogger(__name__)

class TransactionStateServicer(TransactionStateServiceServicer):
    """
    gRPC network boundary controller translating incoming wire payloads 
    into core state engine operational transitions.
    """
    def __init__(self, engine: StateEngine):
        self.engine = engine

    async def FreezeTransaction(
        self, request, context
    ) -> FreezeResponse:
        try:
            tx_id, expires_at = await self.engine.freeze_new_transaction(
                user_id=request.user_id,
                serialized_intent=request.serialized_intent_payload,
                serialized_risk=request.serialized_risk_profile,
                ttl_seconds=request.ttl_seconds
            )
            return FreezeResponse(transaction_id=tx_id, expires_at=expires_at)
        except Exception as e:
            logger.error(f"FreezeTransaction rpc failure: {e}")
            await context.abort(grpc.StatusCode.INTERNAL, str(e))

    async def GetTransaction(
        self, request, context
    ) -> GetTransactionResponse:
        tx = await self.engine.get_active_transaction(request.transaction_id)
        if not tx:
            await context.abort(
                grpc.StatusCode.NOT_FOUND, 
                f"Transaction {request.transaction_id} not found or fully purged."
            )
        return GetTransactionResponse(transaction=tx)

    async def MutateTransactionStatus(
        self, request, context
    ) -> MutateStatusResponse:
        try:
            success, current_status = await self.engine.mutate_transaction_status(
                transaction_id=request.transaction_id,
                expected_current=request.expected_current_status,
                target_status=request.target_status
            )
            return MutateStatusResponse(success=success, current_status=current_status)
        except Exception as e:
            logger.error(f"MutateTransactionStatus rpc failure: {e}")
            await context.abort(grpc.StatusCode.INTERNAL, str(e))


async def serve():
    """
    Asynchronous runner setup to manage the lifetime pool loops of the gRPC server.
    """
    # Initialize dependency chain bottom-up
    repository = TransactionRepository()
    engine = StateEngine(repository)
    servicer = TransactionStateServicer(engine)

    server = grpc.aio.server()
    add_TransactionStateServiceServicer_to_server(servicer, server)
    
    listen_addr = f"[::]:{settings.GRPC_PORT}"
    server.add_insecure_port(listen_addr)
    
    logger.info(f"FinGuard State Service starting async loop on {listen_addr}")
    await server.start()
    
    try:
        await server.wait_for_termination()
    except asyncio.CancelledError:
        logger.info("Shutdown signal caught. Cleaning connection states...")
        await server.stop(grace=5)

if __name__ == "__main__":
    try:
        asyncio.run(serve())
    except KeyboardInterrupt:
        logger.info("Server forced stop by operator execution context.")