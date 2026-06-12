import time
import uuid
import secrets
import logging
from config import settings
from src.repository import TransactionRepository
from generated.state_pb2 import CachedTransaction, TransactionStatus

logger = logging.getLogger(__name__)

class StateEngine:
    def __init__(self, repository: TransactionRepository):
        self.repo = repository

    async def freeze_new_transaction(
        self, 
        user_id: str, 
        serialized_intent: bytes, 
        serialized_risk: bytes, 
        ttl_seconds: int = None
    ) -> tuple[str, int]:
        """
        Creates a brand-new hostage transaction envelope in a PENDING state,
        stamping it with cryptographic salt and precise expiration timelines.
        """
        transaction_id = f"tx_{uuid.uuid4().hex}"
        ttl = ttl_seconds if ttl_seconds else settings.DEFAULT_TTL_SECONDS
        
        current_time = int(time.time())
        expires_at = current_time + ttl

        # Generate unique challenge salt for down-stream verification validation
        challenge_salt = secrets.token_hex(16)

        # Build structural model
        tx = CachedTransaction(
            transaction_id=transaction_id,
            user_id=user_id,
            status=TransactionStatus.PENDING_USER_PIN, # Defaulting baseline context
            serialized_intent_payload=serialized_intent,
            serialized_risk_profile=serialized_risk,
            created_at=current_time,
            expires_at=expires_at,
            challenge_salt=challenge_salt
        )

        success = await self.repo.save_transaction(tx, ttl_seconds=ttl)
        if not success:
            raise RuntimeError("Database write failure while freezing transaction context.")

        return transaction_id, expires_at

    async def get_active_transaction(self, transaction_id: str) -> CachedTransaction:
        """
        Fetches an in-flight transaction. Evaluates TTL dynamically at runtime 
        to ensure expired entries are handled correctly even if Redis eviction hasn't run.
        """
        tx = await self.repo.get_transaction(transaction_id)
        if not tx:
            return None

        # Hard Guardrail Check: Dynamic timestamp boundary evaluation
        if int(time.time()) >= tx.expires_at:
            logger.warning(f"Transaction {transaction_id} accessed past absolute expiry. Mutating to EXPIRED.")
            tx.status = TransactionStatus.EXPIRED
            await self.repo.save_transaction(tx, ttl_seconds=60) # Keep around briefly as dead record
            return tx

        return tx

    async def mutate_transaction_status(
        self, 
        transaction_id: str, 
        expected_current: TransactionStatus, 
        target_status: TransactionStatus
    ) -> tuple[bool, TransactionStatus]:
        """
        Executes a safe Compare-And-Swap (CAS) style state transition matrix.
        Protects against double-submission replays and out-of-order execution loops.
        """
        tx = await self.get_active_transaction(transaction_id)
        if not tx:
            return False, TransactionStatus.STATUS_UNKNOWN

        # Guardrail: Current status must match the Gateway's expected state
        if tx.status != expected_current:
            logger.warning(
                f"State mismatch for {transaction_id}: expected {expected_current}, found {tx.status}."
            )
            return False, tx.status

        # Guardrail: Validate legal destination tracks
        if tx.status in [TransactionStatus.EXPIRED, TransactionStatus.REJECTED_BY_USER, TransactionStatus.EXECUTED]:
            logger.error(f"Terminal state modification attempt blocked for transaction {transaction_id}.")
            return False, tx.status

        # Execute State Flip
        tx.status = target_status
        
        # If transitioning to a finalized state, update the cache retention timeline
        remaining_ttl = max(1, tx.expires_at - int(time.time()))
        if target_status in [TransactionStatus.APPROVED, TransactionStatus.EXECUTED]:
            remaining_ttl = 300 # Keep for 5 minutes to let Executor finish step 6 smoothly

        success = await self.repo.save_transaction(tx, ttl_seconds=remaining_ttl)
        return success, tx.status