"""Feature engineering and decision logic for NovaPay fraud scoring."""

from __future__ import annotations

import numpy as np
import pandas as pd

from api.model_loader import ModelLoadError, ModelRegistry
from api.schemas import TransactionPayload


def transaction_to_dataframe(payload: TransactionPayload) -> pd.DataFrame:
    """Convert a validated request payload into a one-row model input frame."""

    row = payload.model_dump()
    row["timestamp"] = pd.to_datetime(row["timestamp"])
    frame = pd.DataFrame([row])
    return add_engineered_features(frame)


def add_engineered_features(frame: pd.DataFrame) -> pd.DataFrame:
    """Create Day 6-style engineered features expected by the trained model."""

    df = frame.copy()
    timestamp = pd.to_datetime(df["timestamp"])

    # Time-based features
    df["transaction_hour"] = timestamp.dt.hour
    df["weekday"] = timestamp.dt.weekday
    df["is_weekend"] = df["weekday"].isin([5, 6]).astype(int)
    df["is_night_transaction"] = df["transaction_hour"].between(0, 5).astype(int)

    # Geography and corridor features
    df["country_mismatch_flag"] = (df["home_country"] != df["ip_country"]).astype(int)
    df["corridor"] = df["source_currency"].astype(str) + "_to_" + df["dest_currency"].astype(str)

    df["corridor_risk_band"] = pd.cut(
        df["corridor_risk"],
        bins=[-np.inf, 0.33, 0.66, np.inf],
        labels=["low", "medium", "high"],
    ).astype(str)

    # Chargeback grouping
    df["chargeback_group"] = pd.cut(
        df["chargeback_history_count"],
        bins=[-np.inf, 0, 2, np.inf],
        labels=["none", "some", "high"],
    ).astype(str)

    # Velocity and risk flags
    df["high_velocity_1h_flag"] = (df["txn_velocity_1h"] >= 5).astype(int)
    df["high_velocity_24h_flag"] = (df["txn_velocity_24h"] >= 20).astype(int)
    df["any_velocity_risk_flag"] = (
        (df["high_velocity_1h_flag"] == 1) | (df["high_velocity_24h_flag"] == 1)
    ).astype(int)

    df["high_ip_risk_flag"] = (df["ip_risk_score"] >= 0.75).astype(int)
    df["low_device_trust_flag"] = (df["device_trust_score"] <= 0.30).astype(int)

    # Customer-history features.
    # In real deployment these would usually come from a feature store.
    # For this Day 8 API demo, safe defaults are used for single-transaction scoring.
    df["customer_transaction_count"] = df.get("customer_transaction_count", 1)
    df["customer_total_amount"] = df.get("customer_total_amount", df["amount_usd"])
    df["customer_avg_amount"] = df.get("customer_avg_amount", df["amount_usd"])
    df["customer_max_amount"] = df.get("customer_max_amount", df["amount_usd"])
    df["customer_amount_std"] = df.get("customer_amount_std", 0)
    df["customer_recency_days"] = df.get("customer_recency_days", df["account_age_days"])

    df["amount_to_customer_avg"] = (
        df["amount_usd"] / df["customer_avg_amount"].replace(0, 1)
    )

    # Device-history features.
    # In production these would be derived from historical device behaviour.
    df["device_transaction_count"] = df.get("device_transaction_count", 1)
    df["device_avg_trust_score"] = df.get(
        "device_avg_trust_score",
        df["device_trust_score"],
    )

    df["device_trust_band"] = pd.cut(
        df["device_trust_score"],
        bins=[-np.inf, 0.30, 0.70, np.inf],
        labels=["low", "medium", "high"],
    ).astype(str)

    return df


def _fraud_probability(model: object, frame: pd.DataFrame) -> float:
    if hasattr(model, "predict_proba"):
        probabilities = model.predict_proba(frame)
        return float(probabilities[0][1])

    if hasattr(model, "decision_function"):
        score = float(model.decision_function(frame)[0])
        return float(1 / (1 + np.exp(-score)))

    prediction = model.predict(frame)
    return float(prediction[0])


def _decision(probability: float, threshold: float) -> str:
    if probability >= 0.90:
        return "hold_and_investigate"
    if probability >= threshold:
        return "manual_review"
    return "approve"


def _reason(payload: TransactionPayload, probability: float, threshold: float) -> str:
    reasons: list[str] = []

    if payload.txn_velocity_1h >= 5 or payload.txn_velocity_24h >= 20:
        reasons.append("high transaction velocity")
    if payload.ip_risk_score >= 0.75:
        reasons.append("high IP risk score")
    if payload.device_trust_score <= 0.30:
        reasons.append("low device trust score")
    if payload.location_mismatch:
        reasons.append("location mismatch")
    if payload.chargeback_history_count > 0:
        reasons.append("previous chargeback history")
    if payload.corridor_risk >= 0.70:
        reasons.append("high corridor risk")
    if payload.risk_score_internal >= 0.80:
        reasons.append("unusual high internal risk score")

    if reasons:
        return "Transaction flagged for " + ", ".join(reasons) + "."
    if probability >= threshold:
        return "Transaction requires review due to elevated fraud probability."
    return "Transaction appears consistent with approved activity."


def score_transaction(payload: TransactionPayload, registry: ModelRegistry) -> dict[str, object]:
    """Run model inference and return the API response payload."""

    if not registry.model_loaded:
        message = registry.load_error or (
            "Model is not loaded. Generate models/day6/best_advanced_model.joblib "
            "by running 06_advanced_models.ipynb first."
        )
        raise ModelLoadError(message)

    frame = transaction_to_dataframe(payload)
    probability = round(_fraud_probability(registry.model, frame), 4)
    prediction = "fraud" if probability >= registry.threshold else "legitimate"

    return {
        "transaction_id": payload.transaction_id,
        "prediction": prediction,
        "fraud_probability": probability,
        "confidence_score": probability if prediction == "fraud" else round(1 - probability, 4),
        "decision": _decision(probability, registry.threshold),
        "reason": _reason(payload, probability, registry.threshold),
        "model_version": registry.model_version,
    }