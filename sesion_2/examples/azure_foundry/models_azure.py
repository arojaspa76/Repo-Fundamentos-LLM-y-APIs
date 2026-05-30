"""Schemas Pydantic — API de Detección de Fraude con Azure AI Foundry"""

from enum import Enum
from typing import Optional
from pydantic import BaseModel, Field


class FraudVerdict(str, Enum):
    APPROVE = "APROBAR"
    REVIEW  = "REVISAR"
    BLOCK   = "BLOQUEAR"


class CardInfo(BaseModel):
    last_four: str = Field(..., min_length=4, max_length=4)
    card_type: str = Field(..., example="credit")
    issuing_country: str = Field(..., example="CO")


class MerchantInfo(BaseModel):
    name: str
    category: str = Field(..., example="electronics")
    country: str = Field(..., example="US")
    city: str = Field(..., example="Miami")


class UserProfile(BaseModel):
    user_id: str
    avg_transaction_usd: float = Field(..., ge=0)
    typical_countries: list[str] = Field(default=["CO"])
    transactions_last_24h: int = Field(default=0, ge=0)
    account_age_days: int = Field(default=0, ge=0)


class TransactionRequest(BaseModel):
    transaction_id: str = Field(..., example="TXN-2024-001847")
    amount_usd: float = Field(..., gt=0)
    currency: str = Field(default="USD")
    card: CardInfo
    merchant: MerchantInfo
    user_profile: UserProfile
    timestamp: Optional[str] = Field(default=None, example="2024-12-15T14:32:00Z")
    device_fingerprint: Optional[str] = Field(default=None)

    model_config = {
        "json_schema_extra": {
            "example": {
                "transaction_id": "TXN-2024-001847",
                "amount_usd": 1250.0,
                "currency": "USD",
                "card": {"last_four": "4521", "card_type": "credit", "issuing_country": "CO"},
                "merchant": {"name": "Amazon.com", "category": "online_retail", "country": "US", "city": "Seattle"},
                "user_profile": {
                    "user_id": "USR-789012",
                    "avg_transaction_usd": 95.0,
                    "typical_countries": ["CO", "US"],
                    "transactions_last_24h": 2,
                    "account_age_days": 730
                },
                "timestamp": "2024-12-15T14:32:00Z"
            }
        }
    }


class BatchTransactionRequest(BaseModel):
    transactions: list[TransactionRequest] = Field(..., max_length=50)


class FraudSignal(BaseModel):
    description: str


class FraudAnalysisResponse(BaseModel):
    transaction_id: str
    fraud_verdict: str
    fraud_probability: float = Field(ge=0.0, le=1.0)
    fraud_signals: list[FraudSignal]
    explanation: str
    recommended_action: str
    model_used: str
    processing_time_ms: float
    azure_request_id: str


class BatchFraudResponse(BaseModel):
    total_analyzed: int
    flagged_count: int
    blocked_count: int
    average_processing_ms: float
    results: list[FraudAnalysisResponse]


class HealthResponseAzure(BaseModel):
    status: str
    azure_connected: bool
    model: str
    endpoint: str
    uptime_seconds: float
    azure_region: str
