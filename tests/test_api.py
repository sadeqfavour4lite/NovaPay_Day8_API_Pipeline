from fastapi.testclient import TestClient

from api.main import app


SAMPLE_PAYLOAD = {
    "transaction_id": "TX12345",
    "customer_id": "CUST1001",
    "timestamp": "2026-07-03T10:15:00Z",
    "home_country": "GB",
    "source_currency": "GBP",
    "dest_currency": "NGN",
    "channel": "mobile_app",
    "amount_src": 750.0,
    "amount_usd": 950.0,
    "fee": 8.5,
    "exchange_rate_src_to_dest": 1850.25,
    "device_id": "DEV-7788",
    "new_device": True,
    "ip_address": "203.0.113.10",
    "ip_country": "NG",
    "location_mismatch": True,
    "ip_risk_score": 0.86,
    "kyc_tier": "tier_2",
    "account_age_days": 24,
    "device_trust_score": 0.22,
    "chargeback_history_count": 1,
    "risk_score_internal": 0.84,
    "txn_velocity_1h": 7,
    "txn_velocity_24h": 28,
    "corridor_risk": 0.78,
}


def test_health_reports_model_status() -> None:
    with TestClient(app) as client:
        response = client.get("/health")

    assert response.status_code == 200
    body = response.json()
    assert body["status"] == "ok"
    assert isinstance(body["model_loaded"], bool)


def test_score_valid_transaction() -> None:
    with TestClient(app) as client:
        response = client.post("/score", json=SAMPLE_PAYLOAD)

    assert response.status_code == 200
    body = response.json()
    assert body["transaction_id"] == SAMPLE_PAYLOAD["transaction_id"]
    assert body["prediction"] in {"fraud", "legitimate"}
    assert 0 <= body["fraud_probability"] <= 1
    assert 0 <= body["confidence_score"] <= 1
    assert body["decision"] in {"approve", "manual_review", "hold_and_investigate"}
    assert body["model_version"] == "day6_best_advanced_model"


def test_score_rejects_invalid_payload() -> None:
    invalid_payload = SAMPLE_PAYLOAD | {
        "transaction_id": "",
        "amount_usd": -25,
        "ip_risk_score": 1.5,
    }

    with TestClient(app) as client:
        response = client.post("/score", json=invalid_payload)

    assert response.status_code == 422
