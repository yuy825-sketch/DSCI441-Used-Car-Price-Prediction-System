from __future__ import annotations

import argparse
from pathlib import Path

import matplotlib.pyplot as plt
import numpy as np
import pandas as pd
import seaborn as sns

from dsci441_used_car.data import CleanSpec, DEFAULT_FEATURES, clean_dataset, load_vehicles_csv


def _save(fig, path: Path) -> None:
    path.parent.mkdir(parents=True, exist_ok=True)
    fig.tight_layout()
    fig.savefig(path, dpi=200)
    plt.close(fig)


def main() -> int:
    parser = argparse.ArgumentParser()
    parser.add_argument("--csv", type=Path, default=Path("data/craigslist/vehicles.csv"))
    parser.add_argument("--out-dir", type=Path, default=Path("results/dataset"))
    parser.add_argument("--max-rows", type=int, default=200000)
    args = parser.parse_args()

    df = load_vehicles_csv(args.csv)
    df = clean_dataset(df, target="price", features=DEFAULT_FEATURES, spec=CleanSpec())
    if len(df) > args.max_rows:
        df = df.sample(n=int(args.max_rows), random_state=0).reset_index(drop=True)

    out = args.out_dir
    out.mkdir(parents=True, exist_ok=True)

    # Missingness
    miss = df.isna().mean().sort_values(ascending=False)
    top = miss.head(20)
    fig, ax = plt.subplots(figsize=(8.8, 6.2))
    ax.barh(top.index[::-1], (top.values[::-1] * 100.0), color="#4C72B0", alpha=0.9)
    ax.set_title("Top missingness (sample after cleaning)")
    ax.set_xlabel("Missing (%)")
    ax.set_ylabel("")
    _save(fig, out / "missingness_top20.png")

    # Price by year (median + IQR)
    if "year" in df.columns:
        g = df.dropna(subset=["year"]).copy()
        g["year"] = g["year"].astype(int)
        grp = g.groupby("year")["price"]
        years = np.array(sorted(grp.groups.keys()))
        q25 = grp.quantile(0.25).reindex(years).to_numpy()
        q50 = grp.quantile(0.50).reindex(years).to_numpy()
        q75 = grp.quantile(0.75).reindex(years).to_numpy()

        fig, ax = plt.subplots(figsize=(9.2, 4.8))
        ax.fill_between(years, q25, q75, color="#55A868", alpha=0.25, label="IQR")
        ax.plot(years, q50, color="#55A868", linewidth=2.0, label="Median")
        ax.set_title("Price vs Year (median and IQR)")
        ax.set_xlabel("Year")
        ax.set_ylabel("Price (USD)")
        ax.set_ylim(bottom=0)
        ax.legend(loc="upper left")
        _save(fig, out / "price_by_year.png")

    # Price by condition (boxplot)
    if "condition" in df.columns:
        c = df["condition"].value_counts(dropna=True).head(8).index.tolist()
        d = df[df["condition"].isin(c)].copy()
        fig, ax = plt.subplots(figsize=(9.0, 4.8))
        sns.boxplot(data=d, x="condition", y="price", ax=ax, showfliers=False)
        ax.set_yscale("log")
        ax.set_title("Price by Condition (log y, no fliers)")
        ax.set_xlabel("Condition")
        ax.set_ylabel("Price (USD, log scale)")
        ax.tick_params(axis="x", rotation=20)
        _save(fig, out / "price_by_condition_box.png")

    # Price by fuel
    if "fuel" in df.columns:
        c = df["fuel"].value_counts(dropna=True).head(8).index.tolist()
        d = df[df["fuel"].isin(c)].copy()
        fig, ax = plt.subplots(figsize=(8.2, 4.8))
        sns.boxplot(data=d, x="fuel", y="price", ax=ax, showfliers=False)
        ax.set_yscale("log")
        ax.set_title("Price by Fuel Type (log y, no fliers)")
        ax.set_xlabel("Fuel")
        ax.set_ylabel("Price (USD, log scale)")
        _save(fig, out / "price_by_fuel_box.png")

    # Odometer distribution
    if "odometer" in df.columns:
        odo = df["odometer"].dropna().to_numpy(dtype=np.float64)
        fig, ax = plt.subplots(figsize=(8.2, 4.4))
        ax.hist(odo, bins=80, color="#C44E52", alpha=0.85)
        ax.set_title("Odometer distribution")
        ax.set_xlabel("Odometer (miles)")
        ax.set_ylabel("Count")
        _save(fig, out / "odometer_hist.png")

    # Mileage intensity vs price
    if "miles_per_year" in df.columns:
        d = df.dropna(subset=["miles_per_year"]).copy()
        d = d.sample(n=min(len(d), 60000), random_state=0)
        fig, ax = plt.subplots(figsize=(8.2, 4.8))
        ax.scatter(d["miles_per_year"], d["price"], s=6, alpha=0.12)
        ax.set_title("Price vs Miles/Year (sample)")
        ax.set_xlabel("Miles per year")
        ax.set_ylabel("Price (USD)")
        ax.set_yscale("log")
        _save(fig, out / "price_vs_miles_per_year.png")

    print("Wrote:", out / "missingness_top20.png")
    if (out / "price_by_year.png").exists():
        print("Wrote:", out / "price_by_year.png")
    if (out / "price_by_condition_box.png").exists():
        print("Wrote:", out / "price_by_condition_box.png")
    if (out / "price_by_fuel_box.png").exists():
        print("Wrote:", out / "price_by_fuel_box.png")
    if (out / "odometer_hist.png").exists():
        print("Wrote:", out / "odometer_hist.png")
    if (out / "price_vs_miles_per_year.png").exists():
        print("Wrote:", out / "price_vs_miles_per_year.png")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())

