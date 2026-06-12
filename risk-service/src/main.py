import grpc
import logging
from concurrent import futures
from src.config import settings
from generated import risk_pb2_grpc
from src.grpc.risk_servicer import RiskServicer

# Setup clear informative log framing
logging.basicConfig(
    level=logging.INFO,
    format="%(asctime)s [%(levelname)s] %(name)s: %(message)s"
)
logger = logging.getLogger(__name__)

def serve():
    """
    Starts and spins up the gRPC Risk Service Server thread loop wrapper.
    """
    server = grpc.server(futures.ThreadPoolExecutor(max_workers=10))
    
    # Bind service endpoints handlers
    risk_pb2_grpc.add_RiskServiceServicer_to_server(RiskServicer(), server)
    
    listen_addr = f"[::]:{settings.GRPC_PORT}"
    server.add_insecure_port(listen_addr)
    
    logger.info(f"Starting Finguard Risk Engine Microservice on {listen_addr}...")
    server.start()
    
    try:
        server.wait_for_termination()
    except KeyboardInterrupt:
        logger.info("Termination signal caught. Stopping gRPC server gracefully...")
        server.stop(grace=5)

if __name__ == "__main__":
    serve()