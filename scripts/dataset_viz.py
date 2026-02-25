from __future__ import annotations

import argparse
from pathlib import Path

import matplotlib.pyplot as plt
import numpy as np
import pandas as pd
import seaborn as sns

from dsci441_used_car.data import CleanSpec, DEFAULT_FEATURES, clean_dataset, load_vehicles_csv


def main() -> int:
    parser = argparse.ArgumentParser()
    parser.add_argument("--csv", type=Path, default=Path("data/craigslist/vehicles.csv"))
    parser.add_argument("--out-dir", type=Path, default=Path("results/dataset"))
    parser.add_argument("--max-rows", type=int, default=120000)
    args = parser.parse_args()

    df = load_vehicles_csv(args.csv)
    df = clean_dataset(df, target="price", features=DEFAULT_FEATURES, spec=CleanSpec())
    if len(df) > args.max_rows:
        df = df.sample(n=int(args.max_rows), random_state=0).reset_index(drop=True)

    args.out_dir.mkdir(parents=True, exist_ok=True)

    # Price distribution (log scale x)
    fig, ax = plt.subplots(figsize=(6.6, 4.2))
    price = df["price"].to_numpy(dtype=np.float64)
    ax.hist(price, bins=80, color="#4C72B0", alpha=0.85)
    ax.set_xscale("log")
    ax.set_title("Price distribution (log x-axis)")
    ax.set_xlabel("Price (USD)")
    ax.set_ylabel("Count")
    fig.tight_layout()
    fig.savefig(args.out_dir / "price_hist_logx.png", dpi=200)
    plt.close(fig)

    # Odometer vs price
    fig, ax = plt.subplots(figsize=(6.6, 4.8))
    ax.scatter(df["odometer"], df["price"], s=6, alpha=0.15)
    ax.set_title("Price vs Odometer")
    ax.set_xlabel("Odometer (miles)")
    ax.set_ylabel("Price (USD)")
    fig.tight_layout()
    fig.savefig(args.out_dir / "price_vs_odometer.png", dpi=200)
    plt.close(fig)

    # Manufacturer frequency (top 25)
    top = df["manufacturer"].value_counts().head(25)
    fig, ax = plt.subplots(figsize=(8.2, 5.6))
    sns.barplot(x=top.values, y=top.index, ax=ax, color="#55A868")
    ax.set_title("Top manufacturers (count)")
    ax.set_xlabel("Count")
    ax.set_ylabel("Manufacturer")
    fig.tight_layout()
    fig.savefig(args.out_dir / "manufacturer_top25.png", dpi=200)
    plt.close(fig)

    print("Wrote:", args.out_dir / "price_hist_logx.png")
    print("Wrote:", args.out_dir / "price_vs_odometer.png")
    print("Wrote:", args.out_dir / "manufacturer_top25.png")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())

