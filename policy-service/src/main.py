import logging
import signal
import sys
import time
from concurrent import futures
import grpc

from src.config import settings
from src.grpc.policy_servicer import PolicyServicer
from generated import policy_pb2_grpc

# Configure system execution logging format
logging.basicConfig(
    level=logging.INFO,
    format="%(asctime)s [%(levelname)s] %(name)s: %(message)s",
    handlers=[logging.StreamHandler(sys.stdout)]
)
logger = logging.getLogger("finguard.policy_server")


def serve():
    """
    Initializes, configures, and hosts the live gRPC Policy Service server execution loop.
    """
    logger.info("Bootstrapping Finguard Policy Enforcement Engine...")

    # Create a gRPC server optimized with a concurrent execution thread pool
    server = grpc.server(futures.ThreadPoolExecutor(max_workers=10))

    # Register our unpacked custom servicer endpoint into the gRPC routing stack
    policy_pb2_grpc.add_PolicyServiceServicer_to_server(PolicyServicer(), server)

    # Bind to our clean network host parameter
    server_address = f"[::]:{settings.GRPC_PORT}"
    server.add_insecure_port(server_address)
    
    logger.info(f"Policy Service successfully bound to network interface: {server_address}")
    server.start()

    # Define a clean inner handler function to trap runtime system execution halts
    def handle_graceful_shutdown(signum, frame):
        logger.info(f"Shutdown signal received (Signal Code: {signum}). Terminating channels...")
        # Give current processing threads a 5-second grace period to finish active evaluations
        stop_event = server.stop(grace=5)
        stop_event.wait()
        logger.info("Policy Engine execution thread pools released. Safe exit completed.")
        sys.exit(0)

    # Register OS signal traps for execution orchestration containment
    signal.signal(signal.SIGTERM, handle_graceful_shutdown)
    signal.signal(signal.SIGINT, handle_graceful_shutdown)

    # Keep the main process thread alive until an explicit termination occurs
    try:
        while True:
            time.sleep(86400)  # Sleep intervals to maintain baseline idle states
    except Exception as e:
        logger.critical(f"Server execution lifecycle crashed unexpectedly: {str(e)}")
        server.stop(grace=0)


if __name__ == "__main__":
    serve()