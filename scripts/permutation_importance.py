from __future__ import annotations

import argparse
import json
from pathlib import Path

import joblib
import matplotlib.pyplot as plt
import numpy as np
import pandas as pd
from sklearn.inspection import permutation_importance
from sklearn.model_selection import train_test_split

from dsci441_used_car.data import CleanSpec, clean_dataset, load_vehicles_csv


def _load_json(path: Path) -> dict:
    return json.loads(path.read_text(encoding="utf-8"))


def _save(fig, path: Path) -> None:
    path.parent.mkdir(parents=True, exist_ok=True)
    fig.tight_layout()
    fig.savefig(path, dpi=200)
    plt.close(fig)


def _prepare_xy(df: pd.DataFrame, cfg: dict) -> tuple[pd.DataFrame, np.ndarray, list[str]]:
    dataset_cfg = cfg["dataset"]
    target = str(dataset_cfg.get("target", "price"))
    features = list(dataset_cfg["features"])
    if "car_age" in df.columns and "car_age" not in features:
        features.append("car_age")
    if "miles_per_year" in df.columns and "miles_per_year" not in features:
        features.append("miles_per_year")
    X = df[features]
    y = df[target].to_numpy(dtype=np.float64)
    return X, y, features


def main() -> int:
    parser = argparse.ArgumentParser()
    parser.add_argument("--run-dir", type=Path, required=True)
    parser.add_argument("--csv", type=Path, default=Path("data/craigslist/vehicles.csv"))
    parser.add_argument("--out-dir", type=Path, default=Path("results"))
    parser.add_argument("--tag", type=str, default=None)
    parser.add_argument("--max-test-rows", type=int, default=8000)
    parser.add_argument("--repeats", type=int, default=3)
    args = parser.parse_args()

    cfg = _load_json(args.run_dir / "config.json")
    dataset_cfg = cfg["dataset"]

    spec = CleanSpec(
        min_price=float(dataset_cfg.get("min_price", 100)),
        max_price=float(dataset_cfg.get("max_price", 200000)),
        min_year=int(dataset_cfg.get("min_year", 1970)),
        max_year=int(dataset_cfg.get("max_year", 2026)),
        max_odometer=float(dataset_cfg.get("max_odometer", 500000)),
    )
    df_raw = load_vehicles_csv(args.csv, sample_n=dataset_cfg.get("sample_n", None))
    df = clean_dataset(df_raw, target=str(dataset_cfg.get("target", "price")), features=list(dataset_cfg["features"]), spec=spec)

    X, y, features = _prepare_xy(df, cfg)
    split_cfg = cfg.get("split", {}) or {}
    test_size = float(split_cfg.get("test_size", 0.2))
    seed = int(split_cfg.get("seed", 441))

    X_train, X_test, y_train, y_test = train_test_split(X, y, test_size=test_size, random_state=seed)
    _ = X_train, y_train  # unused, but left for clarity

    if len(X_test) > args.max_test_rows:
        X_test = X_test.sample(n=int(args.max_test_rows), random_state=0).reset_index(drop=True)
        y_test = np.asarray(y_test, dtype=np.float64)[: len(X_test)]

    model = joblib.load(args.run_dir / "model.joblib")

    print("Computing permutation importance...")
    pi = permutation_importance(
        model,
        X_test,
        y_test,
        scoring="r2",
        n_repeats=int(args.repeats),
        random_state=0,
        n_jobs=-1,
    )

    imp = pd.DataFrame(
        {
            "feature": features,
            "importance_mean": pi.importances_mean,
            "importance_std": pi.importances_std,
        }
    ).sort_values("importance_mean", ascending=False)

    suffix = f"_{args.tag}" if args.tag else ""
    out_csv = args.out_dir / f"perm_importance{suffix}.csv"
    out_png = args.out_dir / f"perm_importance{suffix}.png"
    imp.to_csv(out_csv, index=False)

    top = imp.head(25).iloc[::-1]
    fig, ax = plt.subplots(figsize=(9.2, 6.6))
    ax.barh(top["feature"], top["importance_mean"], xerr=top["importance_std"], color="#4C72B0", alpha=0.9)
    ax.set_title("Permutation importance (R² decrease, higher is more important)")
    ax.set_xlabel("Importance (mean ± std)")
    ax.set_ylabel("")
    _save(fig, out_png)

    print("Wrote:", out_csv)
    print("Wrote:", out_png)
    return 0


if __name__ == "__main__":
    raise SystemExit(main())

