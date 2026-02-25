from __future__ import annotations

from dataclasses import dataclass
from pathlib import Path

import numpy as np
import pandas as pd


DEFAULT_FEATURES: list[str] = [
    "year",
    "odometer",
    "manufacturer",
    "condition",
    "fuel",
    "transmission",
    "drive",
    "type",
    "paint_color",
    "state",
]


@dataclass(frozen=True)
class CleanSpec:
    min_price: float = 100
    max_price: float = 200000
    min_year: int = 1970
    max_year: int = 2026
    max_odometer: float = 500000


def load_vehicles_csv(path: Path, *, sample_n: int | None = None) -> pd.DataFrame:
    if not path.exists():
        raise FileNotFoundError(f"Dataset not found: {path}")
    df = pd.read_csv(path)
    if sample_n is not None:
        df = df.sample(n=int(sample_n), random_state=0).reset_index(drop=True)
    return df


def clean_dataset(df: pd.DataFrame, *, target: str, features: list[str], spec: CleanSpec) -> pd.DataFrame:
    keep_cols = list(dict.fromkeys([target, *features]))
    missing = [c for c in keep_cols if c not in df.columns]
    if missing:
        raise KeyError(f"Missing columns in dataset: {missing}")

    out = df[keep_cols].copy()

    out[target] = pd.to_numeric(out[target], errors="coerce")
    out = out.dropna(subset=[target])

    if "odometer" in out.columns:
        out["odometer"] = pd.to_numeric(out["odometer"], errors="coerce")

    if "year" in out.columns:
        out["year"] = pd.to_numeric(out["year"], errors="coerce").astype("Int64")
        out["car_age"] = (spec.max_year - out["year"]).astype("Int64")
        if "car_age" not in features:
            out = out.assign(car_age=out["car_age"])

    out = out[(out[target] >= spec.min_price) & (out[target] <= spec.max_price)]

    if "year" in out.columns:
        out = out[(out["year"] >= spec.min_year) & (out["year"] <= spec.max_year)]

    if "odometer" in out.columns:
        out = out[(out["odometer"].isna()) | ((out["odometer"] >= 0) & (out["odometer"] <= spec.max_odometer))]

    # Replace obviously empty strings with NaN for consistent imputation.
    for col in out.columns:
        if out[col].dtype == object:
            out[col] = out[col].replace({"": np.nan, "unknown": np.nan})

    out = out.reset_index(drop=True)
    return out

