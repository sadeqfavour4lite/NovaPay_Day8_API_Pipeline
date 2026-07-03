"""Pydantic schemas for NovaPay real-time fraud scoring."""

from datetime import datetime

from pydantic import BaseModel, Field, field_validator


class TransactionPayload(BaseModel):
    """Single transaction payload accepted by the fraud scoring endpoint."""

    transaction_id: str
    customer_id: str
    timestamp: datetime
    home_country: str
    source_currency: str
    dest_currency: str
    channel: str
    amount_src: float = Field(ge=0)
    amount_usd: float = Field(ge=0)
    fee: float = Field(ge=0)
    exchange_rate_src_to_dest: float = Field(gt=0)
    device_id: str
    new_device: bool
    ip_address: str
    ip_country: str
    location_mismatch: bool
    ip_risk_score: float = Field(ge=0, le=1)
    kyc_tier: str
    account_age_days: int = Field(ge=0)
    device_trust_score: float = Field(ge=0, le=1)
    chargeback_history_count: int = Field(ge=0)
    risk_score_internal: float = Field(ge=0, le=1)
    txn_velocity_1h: int = Field(ge=0)
    txn_velocity_24h: int = Field(ge=0)
    corridor_risk: float = Field(ge=0, le=1)

    @field_validator(
        "transaction_id",
        "customer_id",
        "home_country",
        "source_currency",
        "dest_currency",
        "channel",
        "device_id",
        "ip_address",
        "ip_country",
        "kyc_tier",
    )
    @classmethod
    def must_not_be_empty(cls, value: str) -> str:
        if not value or not value.strip():
            raise ValueError("must not be empty")
        return value.strip()


class ScoreResponse(BaseModel):
    """Response returned by the fraud scoring endpoint."""

    transaction_id: str
    prediction: str
    fraud_probability: float
    confidence_score: float
    decision: str
    reason: str
    model_version: str
