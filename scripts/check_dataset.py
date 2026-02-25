from __future__ import annotations

import argparse
from pathlib import Path

import pandas as pd

from dsci441_used_car.data import CleanSpec, DEFAULT_FEATURES, clean_dataset, load_vehicles_csv


def main() -> int:
    parser = argparse.ArgumentParser()
    parser.add_argument("--csv", type=Path, default=Path("data/craigslist/vehicles.csv"))
    parser.add_argument("--sample-n", type=int, default=None)
    args = parser.parse_args()

    df = load_vehicles_csv(args.csv, sample_n=args.sample_n)
    print("Raw rows:", len(df))
    target = "price"
    features = DEFAULT_FEATURES

    spec = CleanSpec()
    cleaned = clean_dataset(df, target=target, features=features, spec=spec)
    print("Clean rows:", len(cleaned))
    print("Columns:", list(cleaned.columns))

    missing = cleaned.isna().mean().sort_values(ascending=False).head(15)
    print("\nTop missingness (fraction):")
    print(missing.to_string())

    return 0


if __name__ == "__main__":
    raise SystemExit(main())

