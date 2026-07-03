"""FastAPI application for NovaPay real-time fraud scoring."""

from contextlib import asynccontextmanager

from fastapi import FastAPI, HTTPException, status

from api.model_loader import registry
from api.schemas import ScoreResponse, TransactionPayload
from api.scoring import ModelLoadError, score_transaction


@asynccontextmanager
async def lifespan(app: FastAPI):
    registry.load()
    yield


app = FastAPI(
    title="NovaPay Fraud Scoring API",
    description="Real-time fraudulent transaction detection API for digital money transfers.",
    version="1.0.0",
    lifespan=lifespan,
)


@app.get("/health")
def health() -> dict[str, object]:
    return {"status": "ok", "model_loaded": registry.model_loaded}


@app.post("/score", response_model=ScoreResponse)
def score(payload: TransactionPayload) -> dict[str, object]:
    try:
        return score_transaction(payload, registry)
    except ModelLoadError as exc:
        raise HTTPException(
            status_code=status.HTTP_503_SERVICE_UNAVAILABLE,
            detail=str(exc),
        ) from exc
