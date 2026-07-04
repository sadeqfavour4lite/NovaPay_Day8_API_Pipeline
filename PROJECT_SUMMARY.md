# NovaPay Fraud Scoring API – Project Summary

## Project Overview

The NovaPay Fraud Scoring API packages a trained machine learning fraud detection model into a production-style REST API using FastAPI.

The service accepts a single digital money-transfer transaction, recreates the engineered features used during model training, performs real-time fraud prediction, and returns an interpretable operational decision suitable for fraud analysts or downstream systems.

The project demonstrates how a trained machine learning model can be deployed as an API while maintaining reproducibility, validation, documentation, and production-ready project structure.

---

# Project Architecture

| Component | Purpose |
|----------|---------|
| `api/main.py` | FastAPI application, startup logic, and API endpoints (`/health`, `/score`) |
| `api/schemas.py` | Pydantic request and response models with input validation |
| `api/model_loader.py` | Loads the trained Day 6 model artifact and fraud threshold |
| `api/scoring.py` | Performs feature engineering, model inference, decision logic, and response generation |
| `models/day6/best_advanced_model.joblib` | Trained fraud detection model |
| `08_api_pipeline.ipynb` | Primary notebook documenting API packaging, validation, testing, and deployment |

---

# Key Features

- FastAPI REST API implementation
- Real-time fraud scoring
- Automatic request validation using Pydantic
- Feature engineering consistent with the Day 6 training pipeline
- Explainable prediction responses
- Health monitoring endpoint
- Swagger and ReDoc interactive documentation
- Docker support
- Automated API smoke tests
- Production-style project structure

---

# Production Readiness Improvements

The following improvements were completed during the API packaging stage:

- Added a root `requirements.txt` for simplified installation.
- Updated dependencies to match the trained model artifact, including:
  - `scikit-learn`
  - `imbalanced-learn`
  - `xgboost`
- Improved Docker packaging to install from the root requirements file.
- Added `.gitignore` and `.dockerignore`.
- Added `api/__init__.py` to support package imports.
- Improved model loading by resolving artifact paths relative to the project root.
- Expanded project documentation, including:
  - README
  - Testing Guide
  - Validation Notes
  - Final Submission Checklist
- Added automated smoke tests covering:
  - Health endpoint
  - Fraud scoring endpoint
  - Validation failures
- Improved notebook documentation while preserving the original model behaviour and prediction logic.

---

# API Endpoints

## GET `/health`

Returns the API status and confirms whether the trained model has been successfully loaded.

---

## POST `/score`

Accepts a single transaction and returns:

- transaction ID
- fraud prediction
- fraud probability
- confidence score
- operational decision
- human-readable explanation
- model version

---

# Validation

The API validates incoming requests before model inference.

Validation includes:

- Required fields
- Non-empty string values
- Valid datetime format
- Non-negative monetary values
- Positive exchange rate
- Boolean flags
- Risk scores constrained between 0 and 1
- Non-negative transaction counts

Invalid requests return an HTTP 422 validation response.

---

# Prediction Workflow

1. Receive transaction payload.
2. Validate request using Pydantic.
3. Recreate engineered features.
4. Load the trained Day 6 model.
5. Generate fraud probability.
6. Apply the operational fraud threshold.
7. Produce prediction and decision.
8. Return an explainable JSON response.

---

# Testing

The API was successfully verified using:

- FastAPI Swagger UI
- Manual fraud and legitimate transaction scenarios
- Validation error testing
- Automated smoke tests using `pytest`

---

# Technologies Used

- Python
- FastAPI
- Pydantic
- Pandas
- NumPy
- Scikit-learn
- Joblib
- Uvicorn
- Docker

---

# Summary

The NovaPay Fraud Scoring API successfully converts a trained fraud detection model into a production-style REST API capable of real-time transaction scoring.

The implementation preserves the original machine learning model while adding robust validation, automated testing, documentation, deployment support, and a maintainable project structure suitable for demonstration and future production deployment.