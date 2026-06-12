import logging
import redis.asyncio as aioredis
from typing import Optional
from config import settings
from generated.state_pb2 import CachedTransaction

logger = logging.getLogger(__name__)

class TransactionRepository:
    def __init__(self):
        """
        Initializes an asynchronous, thread-safe Redis connection pool 
        using configuration constants.
        """
        self.redis_client = aioredis.Redis(
            host=settings.REDIS_HOST,
            port=settings.REDIS_PORT,
            db=settings.REDIS_DB,
            password=settings.REDIS_PASSWORD
        )
        # Prefix keys to keep the Redis namespace clean from other services
        self.key_prefix = "finguard:tx:"

    def _get_key(self, transaction_id: str) -> str:
        return f"{self.key_prefix}{transaction_id}"

    async def save_transaction(self, tx: CachedTransaction, ttl_seconds: int) -> bool:
        """
        Serializes a CachedTransaction protobuf message directly to raw bytes 
        and sets it in Redis with an absolute atomic expiration timeline.
        """
        key = self._get_key(tx.transaction_id)
        # Serialize the structured proto message directly to atomic binary payload
        serialized_bytes = tx.SerializeToString()
        
        try:
            # Set string payload and apply TTL atomically
            await self.redis_client.set(key, serialized_bytes, ex=ttl_seconds)
            return True
        except Exception as e:
            logger.error(f"Failed to write transaction {tx.transaction_id} to Redis: {e}")
            return False

    async def get_transaction(self, transaction_id: str) -> Optional[CachedTransaction]:
        """
        Retrieves raw binary state out of Redis and reconstructs the structured 
        CachedTransaction protobuf message. Returns None if expired or missing.
        """
        key = self._get_key(transaction_id)
        try:
            raw_bytes = await self.redis_client.get(key)
            if not raw_bytes:
                return None
            
            # Rehydrate binary string directly back into object format
            tx = CachedTransaction()
            tx.ParseFromString(raw_bytes)
            return tx
        except Exception as e:
            logger.error(f"Failed to read/parse transaction {transaction_id} from Redis: {e}")
            return None

    async def delete_transaction(self, transaction_id: str) -> bool:
        """
        Explicitly removes a transaction record from the cache pool.
        Useful when tracking terminal state transitions or cleanup routines.
        """
        key = self._get_key(transaction_id)
        try:
            result = await self.redis_client.delete(key)
            return result > 0
        except Exception as e:
            logger.error(f"Failed to delete key {key}: {e}")
            return False

    async def close(self):
        """
        Gracefully closes the underlying Redis connection pool resources.
        Called directly by the gRPC server during shutdown cycles.
        """
        logger.info("Closing Redis asynchronous repository pool connection...")
        await self.redis_client.aclose()