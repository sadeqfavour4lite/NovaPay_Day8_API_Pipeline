# NovaPay Fraud Scoring API

NovaPay Fraud Scoring API is a production-style FastAPI service that scores digital money-transfer transactions for potential fraud.

The API validates a transaction payload, recreates the engineered features used during model training, loads the trained Day 6 machine learning model, and returns a real-time fraud probability, prediction, operational decision, and human-readable explanation.

This repository represents the Day 8 API Packaging deliverable for the NovaPay Fraud Detection project.

---

# Project Structure

```text
.
├── api/
│   ├── __init__.py
│   ├── main.py                  # FastAPI application
│   ├── model_loader.py          # Loads trained model
│   ├── schemas.py              # Pydantic request/response models
│   ├── scoring.py              # Feature engineering & prediction logic
│   └── requirements.txt
│
├── models/
│   └── day6/
│       └── best_advanced_model.joblib
│
├── reports/
│   └── artifacts/
│       └── day8/
│           ├── api_validation_notes.md
│           ├── sample_request.json
│           └── sample_response.json
│
├── tests/
│   └── test_api.py
│
├── 08_api_pipeline.ipynb
├── Dockerfile
├── PROJECT_SUMMARY.md
├── TESTING_GUIDE.md
├── FINAL_SUBMISSION_CHECKLIST.md
├── requirements.txt
└── README.md
```

---

# What the API Does

The API performs the following tasks:

- Accepts a single transaction via REST API
- Validates incoming payloads using Pydantic
- Performs feature engineering identical to the Day 6 model pipeline
- Loads the trained fraud detection model
- Calculates fraud probability
- Applies the operational fraud threshold
- Returns an explainable fraud decision

The API is designed for real-time transaction scoring.

---

# Base URL

When running locally:

```
http://127.0.0.1:8000
```

---

# Interactive API Documentation

### Swagger UI

```
http://127.0.0.1:8000/docs
```

### ReDoc Documentation

```
http://127.0.0.1:8000/redoc
```

---

# API Endpoints

## GET /health

Returns API health status and model availability.

### Example Response

```json
{
  "status": "ok",
  "model_loaded": true
}
```

---

## POST /score

Scores a transaction for fraud.

Example:

```bash
curl -X POST "http://127.0.0.1:8000/score" \
-H "Content-Type: application/json" \
--data @reports/artifacts/day8/sample_request.json
```

---

# Example Successful Response

```json
{
  "transaction_id": "TX12345",
  "prediction": "fraud",
  "fraud_probability": 0.92,
  "confidence_score": 0.92,
  "decision": "hold_and_investigate",
  "reason": "Transaction flagged for high transaction velocity, high IP risk score, low device trust score, location mismatch, previous chargeback history, high corridor risk, unusual high internal risk score.",
  "model_version": "day6_best_advanced_model"
}
```

---

# Request Schema

| Field | Type | Validation |
|-------|------|------------|
| transaction_id | string | Required |
| customer_id | string | Required |
| timestamp | datetime | Required |
| home_country | string | Required |
| source_currency | string | Required |
| dest_currency | string | Required |
| channel | string | Required |
| amount_src | float | >=0 |
| amount_usd | float | >=0 |
| fee | float | >=0 |
| exchange_rate_src_to_dest | float | >0 |
| device_id | string | Required |
| new_device | boolean | Required |
| ip_address | string | Required |
| ip_country | string | Required |
| location_mismatch | boolean | Required |
| ip_risk_score | float | 0–1 |
| kyc_tier | string | Required |
| account_age_days | integer | >=0 |
| device_trust_score | float | 0–1 |
| chargeback_history_count | integer | >=0 |
| risk_score_internal | float | 0–1 |
| txn_velocity_1h | integer | >=0 |
| txn_velocity_24h | integer | >=0 |
| corridor_risk | float | 0–1 |

> **Note**
>
> The API validates data types and required fields but does not enforce predefined lists of countries, currencies, KYC tiers, channels or IP formats.

---

# Installation

Clone the repository and install dependencies.

```bash
python -m venv .venv
```

Activate the environment.

Windows

```bash
.venv\Scripts\activate
```

macOS/Linux

```bash
source .venv/bin/activate
```

Install packages.

```bash
pip install -r requirements.txt
```

---

# Running the API

Start the FastAPI server.

```bash
uvicorn api.main:app --reload
```

The API will be available at

```
http://127.0.0.1:8000
```

Swagger documentation

```
http://127.0.0.1:8000/docs
```

---

# Model Artifact

The API expects the trained model to exist at

```
models/day6/best_advanced_model.joblib
```

If the model cannot be loaded:

- `/health` reports

```json
{
    "model_loaded": false
}
```

- `/score` returns

```
HTTP 503
```

with a descriptive error message.

---

# Running Tests

Execute all automated tests.

```bash
pytest
```

Manual API testing examples are documented in

```
TESTING_GUIDE.md
```

---

# Docker

Build the Docker image.

```bash
docker build -t novapay-fraud-api .
```

Run the container.

```bash
docker run -p 8000:8000 novapay-fraud-api
```

Open Swagger UI.

```
http://127.0.0.1:8000/docs
```

---

# Manual Verification

The API was manually tested using the FastAPI Swagger UI.

The following scenarios were verified successfully:

- ✅ Legitimate transaction
- ✅ High-risk fraudulent transaction
- ✅ Request validation errors
- ✅ Health endpoint
- ✅ Model loading
- ✅ Prediction endpoint
- ✅ Fraud probability calculation
- ✅ Decision logic

All tests returned the expected responses.

---

# Notes for Reviewers

- The primary implementation notebook is **08_api_pipeline.ipynb**.
- The trained model is loaded directly without retraining.
- Feature engineering reproduces the transformations used during model development.
- Customer-history and device-history features unavailable during single transaction inference are safely defaulted within the API.
- The API has been manually tested and validated using the FastAPI Swagger interface.

---

# Technologies Used

- Python 3.10+
- FastAPI
- Pydantic
- Pandas
- NumPy
- Scikit-learn
- Uvicorn
- Joblib
- Docker

---

# Author

NovaPay Fraud Detection Project

Day 8 – API Packaging and Deployment

Built as part of the NovaPay Fraud Detection Machine Learning Pipeline.

## License

This project was developed for educational and portfolio purposes as part of the NovaPay Fraud Detection internship project.
