from pydantic import BaseModel, Field
from enum import IntEnum


class ActionType(IntEnum):
    ACTION_UNSPECIFIED = 0
    CHECK_BALANCE = 1
    TRANSFER = 2
    BUY_CRYPTO = 3
    UNKNOWN_ACTION = 4


class TargetNetwork(IntEnum):
    NETWORK_UNSPECIFIED = 0
    FIAT_BANK_ACH = 1
    CRYPTO_BLOCKCHAIN = 2
    INTERNAL_WALLET = 3


class UrgencyLevel(IntEnum):
    URGENCY_UNSPECIFIED = 0
    STANDARD = 1
    HIGH_URGENCY = 2


class TransactionCategory(IntEnum):
    CATEGORY_UNSPECIFIED = 0
    PEER_TO_PEER = 1
    BILL_PAYMENT = 2
    SPECULATIVE_ASSET = 3


class IntentPayloadSchema(BaseModel):
    action: ActionType = Field(
        default=ActionType.ACTION_UNSPECIFIED,
        description="The action the user wants to perform"
    )
    amount: float = Field(
        default=0.0,
        description="The monetary amount involved in the transaction"
    )
    currency: str = Field(
        default="",
        description="The currency code, e.g. USD, BTC, ETH"
    )
    recipient_alias: str = Field(
        default="",
        description="The alias or name of the recipient, if any"
    )
    target_network: TargetNetwork = Field(
        default=TargetNetwork.NETWORK_UNSPECIFIED,
        description="The network or rails to use for the transaction"
    )
    category: TransactionCategory = Field(
        default=TransactionCategory.CATEGORY_UNSPECIFIED,
        description="The category of the transaction"
    )
    urgency: UrgencyLevel = Field(
        default=UrgencyLevel.URGENCY_UNSPECIFIED,
        description="How urgently the transaction should be processed"
    )
    recipient_is_explicit: bool = Field(
        default=False,
        description="Whether the user explicitly named a recipient"
    )
    is_ambiguous: bool = Field(
        default=False,
        description="Whether the intent is ambiguous and needs clarification"
    )
    status_message: str = Field(
        default="",
        description="Human-readable status or clarification message"
    )

    def to_proto(self):
        from generated.intent_pb2 import IntentPayload
        return IntentPayload(
            action=int(self.action),
            amount=self.amount,
            currency=self.currency,
            recipient_alias=self.recipient_alias,
            target_network=int(self.target_network),
            category=int(self.category),
            urgency=int(self.urgency),
            recipient_is_explicit=self.recipient_is_explicit,
            is_ambiguous=self.is_ambiguous,
            status_message=self.status_message,
        )