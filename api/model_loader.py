"""Model artifact loading for the NovaPay fraud scoring API."""

from __future__ import annotations

import json
import logging
from pathlib import Path
from typing import Any

import joblib

LOGGER = logging.getLogger(__name__)

MODEL_VERSION = "day6_best_advanced_model"
MODEL_PATH = Path("models/day6/best_advanced_model.joblib")
DEFAULT_THRESHOLD = 0.80


class ModelLoadError(RuntimeError):
    """Raised when the required model artifact cannot be loaded."""


def _load_threshold(model_path: Path) -> float:
    """Load a saved threshold if present; otherwise use the Day 8 default."""

    candidate_paths = [
        model_path.with_name("best_threshold.json"),
        model_path.with_name("threshold.json"),
        model_path.with_name("best_threshold.joblib"),
        model_path.with_name("threshold.joblib"),
    ]

    for path in candidate_paths:
        if not path.exists():
            continue

        if path.suffix == ".json":
            with path.open("r", encoding="utf-8") as handle:
                data = json.load(handle)
            value = data.get("threshold", data) if isinstance(data, dict) else data
        else:
            value = joblib.load(path)
            if isinstance(value, dict):
                value = value.get("threshold", DEFAULT_THRESHOLD)

        try:
            threshold = float(value)
        except (TypeError, ValueError):
            LOGGER.warning("Ignoring invalid threshold artifact at %s", path)
            continue

        if 0 < threshold < 1:
            return threshold

        LOGGER.warning("Ignoring out-of-range threshold artifact at %s", path)

    return DEFAULT_THRESHOLD


class ModelRegistry:
    """Holds the loaded model and inference threshold for the API process."""

    def __init__(self, model_path: Path = MODEL_PATH) -> None:
        self.model_path = model_path
        self.model: Any | None = None
        self.threshold = DEFAULT_THRESHOLD
        self.model_version = MODEL_VERSION
        self.load_error: str | None = None

    @property
    def model_loaded(self) -> bool:
        return self.model is not None

    def load(self) -> None:
        """Load the model once at application startup."""

        if not self.model_path.exists():
            self.load_error = (
                f"Model file not found at {self.model_path}. "
                "Generate it by running 06_advanced_models.ipynb first."
            )
            LOGGER.warning(self.load_error)
            return

        try:
            self.model = joblib.load(self.model_path)
            self.threshold = _load_threshold(self.model_path)
            self.load_error = None
            LOGGER.info("Loaded model from %s with threshold %.2f", self.model_path, self.threshold)
        except Exception as exc:  # pragma: no cover - keeps startup diagnostics explicit.
            self.model = None
            self.load_error = f"Failed to load model from {self.model_path}: {exc}"
            LOGGER.exception(self.load_error)


registry = ModelRegistry()
