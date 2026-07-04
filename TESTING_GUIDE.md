# NovaPay Fraud Scoring API – Testing Guide

This guide explains how to install, run, and verify the NovaPay Fraud Scoring API from a fresh clone of the project.

---

# 1. Install Dependencies

From the project root:

```bash
python -m venv .venv
```

Activate the virtual environment.

### Windows

```bash
.venv\Scripts\activate
```

### macOS/Linux

```bash
source .venv/bin/activate
```

Install all required packages.

```bash
pip install -r requirements.txt
```

---

# 2. Verify the Model Artifact

The API expects the trained model at:

```text
models/day6/best_advanced_model.joblib
```

If the model file is missing, generate it by running the Day 6 training notebook before testing the API.

---

# 3. Start the API

Run:

```bash
uvicorn api.main:app --reload
```

Once started, the API will be available at:

```
http://127.0.0.1:8000
```

Interactive documentation:

### Swagger UI

```
http://127.0.0.1:8000/docs
```

### ReDoc

```
http://127.0.0.1:8000/redoc
```

---

# 4. Verify API Health

Open:

```
http://127.0.0.1:8000/health
```

Expected response:

```json
{
    "status": "ok",
    "model_loaded": true
}
```

If `model_loaded` is `false`, confirm that the trained model exists in:

```
models/day6/
```

---

# 5. Manual API Testing

The API can be tested directly from Swagger UI or by using `curl`.

Example:

```bash
curl -X POST "http://127.0.0.1:8000/score" \
-H "Content-Type: application/json" \
--data @reports/artifacts/day8/sample_request.json
```

Expected response:

- HTTP Status **200**
- Valid JSON response
- Fraud probability between **0 and 1**
- Prediction returned
- Operational decision returned
- Human-readable explanation returned

---

# 6. Manual Test Scenarios

The following scenarios were successfully verified during development.

| Test Scenario | Expected Result |
|---------------|-----------------|
| Legitimate transaction | HTTP 200, low fraud probability, `approve` decision |
| High-risk fraud transaction | HTTP 200, high fraud probability, `hold_and_investigate` decision |
| Medium-risk transaction | HTTP 200, `manual_review` or `approve` depending on model score |
| New device from another country | HTTP 200 with location/device risk explanation |
| Invalid payload | HTTP 422 validation error |
| Missing required field | HTTP 422 validation error |
| Negative monetary value | HTTP 422 validation error |
| Risk score greater than 1 | HTTP 422 validation error |

---

# 7. Automated Tests

Run:

```bash
pytest
```

The automated tests verify:

- API startup
- Health endpoint
- Successful fraud scoring
- Invalid request validation
- Response schema

---

# 8. Docker Verification

Build the Docker image.

```bash
docker build -t novapay-fraud-api .
```

Run the container.

```bash
docker run -p 8000:8000 novapay-fraud-api
```

Open:

```
http://127.0.0.1:8000/docs
```

Verify:

- Swagger loads successfully
- `/health` returns HTTP 200
- `/score` returns predictions successfully

---

# Expected API Response

A successful scoring request returns a JSON response similar to:

```json
{
  "transaction_id": "TXN000001",
  "prediction": "fraud",
  "fraud_probability": 0.999,
  "confidence_score": 0.999,
  "decision": "hold_and_investigate",
  "reason": "Transaction flagged for high transaction velocity, high IP risk score, location mismatch, previous chargeback history, high corridor risk, unusual high internal risk score.",
  "model_version": "day6_best_advanced_model"
}
```

---

# Testing Summary

The NovaPay Fraud Scoring API was successfully verified using:

- FastAPI Swagger UI
- ReDoc documentation
- Manual transaction testing
- Automated pytest smoke tests
- Docker deployment testing

The API correctly validates requests, performs feature engineering, loads the trained machine learning model, and returns explainable fraud predictions in real time.