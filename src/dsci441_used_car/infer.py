from __future__ import annotations

from dataclasses import dataclass
from pathlib import Path
from typing import Any

import joblib
import pandas as pd


@dataclass(frozen=True)
class LoadedModel:
    pipeline: Any


def load_run_model(run_dir: Path) -> LoadedModel:
    model_path = run_dir / "model.joblib"
    if not model_path.exists():
        raise FileNotFoundError(f"Model not found: {model_path}")
    pipeline = joblib.load(model_path)
    return LoadedModel(pipeline=pipeline)


def predict_one(pipeline: Any, features: dict) -> float:
    df = pd.DataFrame([features])
    pred = pipeline.predict(df)
    return float(pred[0])

