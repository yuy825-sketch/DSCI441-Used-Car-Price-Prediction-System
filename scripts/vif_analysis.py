from __future__ import annotations

import argparse
from pathlib import Path

import matplotlib.pyplot as plt
import numpy as np
import pandas as pd
import seaborn as sns
from statsmodels.stats.outliers_influence import variance_inflation_factor

from dsci441_used_car.data import CleanSpec, clean_dataset, load_vehicles_csv


def _compute_vif(X: pd.DataFrame) -> pd.DataFrame:
    X = X.copy()
    X = X.replace([np.inf, -np.inf], np.nan).dropna()
    if X.empty or X.shape[1] < 2:
        return pd.DataFrame({"feature": list(X.columns), "vif": []})

    arr = X.to_numpy(dtype=np.float64)
    out = []
    for i, name in enumerate(X.columns):
        out.append({"feature": name, "vif": float(variance_inflation_factor(arr, i))})
    return pd.DataFrame(out).sort_values("vif", ascending=False).reset_index(drop=True)


def main() -> int:
    parser = argparse.ArgumentParser()
    parser.add_argument("--csv", type=Path, default=Path("data/craigslist/vehicles.csv"))
    parser.add_argument("--out-dir", type=Path, default=Path("results/dataset"))
    parser.add_argument("--max-rows", type=int, default=80000, help="Subsample rows for faster VIF/corr")
    args = parser.parse_args()

    df = load_vehicles_csv(args.csv)

    # Keep only numeric signals for VIF (VIF on one-hot expanded high-cardinality cats is usually not meaningful).
    features = ["year", "odometer"]
    df = clean_dataset(df, target="price", features=features, spec=CleanSpec())
    if "car_age" in df.columns:
        features = ["year", "odometer", "car_age"]

    if len(df) > args.max_rows:
        df = df.sample(n=int(args.max_rows), random_state=0).reset_index(drop=True)

    X = df[features].apply(pd.to_numeric, errors="coerce")
    vif = _compute_vif(X)

    args.out_dir.mkdir(parents=True, exist_ok=True)
    vif.to_csv(args.out_dir / "vif_numeric.csv", index=False)

    corr = X.corr(numeric_only=True)
    fig, ax = plt.subplots(figsize=(5.2, 4.6))
    sns.heatmap(corr, annot=True, fmt=".2f", cmap="vlag", center=0.0, ax=ax)
    ax.set_title("Numeric correlation")
    fig.tight_layout()
    fig.savefig(args.out_dir / "corr_numeric.png", dpi=200)
    plt.close(fig)

    print("Wrote:", args.out_dir / "vif_numeric.csv")
    print("Wrote:", args.out_dir / "corr_numeric.png")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())

