from __future__ import annotations

import importlib.util
import sys

import numpy as np
import pandas as pd

from dsci441_used_car.train_utils import fit_from_config


def _check_import(name: str) -> None:
    spec = importlib.util.find_spec(name)
    if spec is None:
        raise RuntimeError(f"Missing dependency: {name}")


def _synthetic_df(n: int = 200) -> pd.DataFrame:
    rng = np.random.default_rng(0)
    df = pd.DataFrame(
        {
            "year": rng.integers(2000, 2026, size=n),
            "odometer": rng.normal(90000, 45000, size=n).clip(0, 350000),
            "manufacturer": rng.choice(["ford", "toyota", "honda"], size=n),
            "condition": rng.choice(["excellent", "good", "fair"], size=n),
            "fuel": rng.choice(["gas", "diesel"], size=n),
            "transmission": rng.choice(["automatic", "manual"], size=n),
            "drive": rng.choice(["fwd", "rwd", "4wd"], size=n),
            "type": rng.choice(["sedan", "suv", "truck"], size=n),
            "paint_color": rng.choice(["black", "white", "silver"], size=n),
            "state": rng.choice(["pa", "nj", "ny"], size=n),
        }
    )
    base = 24000 - 1200 * (2026 - df["year"]) - 0.03 * df["odometer"]
    brand = df["manufacturer"].map({"ford": -800, "toyota": 500, "honda": 300}).astype(float)
    noise = rng.normal(0, 1500, size=n)
    df["price"] = (base + brand + noise).clip(1000, 50000)
    return df


def main() -> int:
    deps = ["numpy", "pandas", "sklearn", "statsmodels", "matplotlib", "seaborn", "joblib", "streamlit"]
    for dep in deps:
        _check_import(dep)

    df = _synthetic_df(250)
    cfg = {
        "dataset": {
            "target": "price",
            "features": [
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
            ],
        },
        "split": {"test_size": 0.2, "seed": 441},
        "preprocess": {"standardize_numeric": True},
        "train": {"log_target": True},
        "model": {"type": "ridge", "alpha": 2.0},
    }
    out = fit_from_config(df=df, cfg=cfg)

    print("OK: imports")
    print("Python:", sys.version.split()[0])
    print("Smoke test metrics (test):", out.metrics["test"])
    return 0


if __name__ == "__main__":
    raise SystemExit(main())

