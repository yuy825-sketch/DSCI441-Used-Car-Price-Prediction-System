from __future__ import annotations

import argparse
import json
import math
from pathlib import Path

import matplotlib.pyplot as plt
import numpy as np


def _rmse(y_true: np.ndarray, y_pred: np.ndarray) -> float:
    return float(math.sqrt(np.mean((y_true - y_pred) ** 2)))


def _mae(y_true: np.ndarray, y_pred: np.ndarray) -> float:
    return float(np.mean(np.abs(y_true - y_pred)))


def _read_json(path: Path) -> dict:
    with path.open("r", encoding="utf-8") as f:
        return json.load(f)


def _percent_within(y_true: np.ndarray, y_pred: np.ndarray, *, dollars: float) -> float:
    err = np.abs(y_true - y_pred)
    return float(np.mean(err <= float(dollars)))


def _percent_within_pct(y_true: np.ndarray, y_pred: np.ndarray, *, pct: float) -> float:
    denom = np.clip(np.abs(y_true), 1.0, None)
    err_pct = np.abs(y_true - y_pred) / denom
    return float(np.mean(err_pct <= float(pct)))


def _quantile_bin_stats(y_true: np.ndarray, y_pred: np.ndarray, *, n_bins: int) -> tuple[np.ndarray, np.ndarray, np.ndarray]:
    y = y_true.astype(np.float64)
    bins = np.quantile(y, np.linspace(0.0, 1.0, int(n_bins) + 1))
    # Ensure strictly increasing edges.
    bins = np.unique(bins)
    if bins.size < 3:
        return np.asarray([]), np.asarray([]), np.asarray([])

    idx = np.digitize(y, bins[1:-1], right=True)
    centers: list[float] = []
    rmses: list[float] = []
    maes: list[float] = []
    for b in range(int(bins.size) - 1):
        mask = idx == b
        if not np.any(mask):
            continue
        lo, hi = float(bins[b]), float(bins[b + 1])
        centers.append((lo + hi) / 2.0)
        rmses.append(_rmse(y_true[mask], y_pred[mask]))
        maes.append(_mae(y_true[mask], y_pred[mask]))
    return np.asarray(centers), np.asarray(rmses), np.asarray(maes)


def _hist_abs_error(abs_err: np.ndarray, out_png: Path) -> None:
    fig, ax = plt.subplots(figsize=(6.2, 4.2))
    ax.hist(abs_err, bins=60, color="#4C72B0", alpha=0.9)
    ax.set_xscale("log")
    ax.set_title("Absolute Error Histogram (Test)")
    ax.set_xlabel("|true - pred| (USD, log scale)")
    ax.set_ylabel("Count")
    fig.tight_layout()
    fig.savefig(out_png, dpi=200)
    plt.close(fig)


def _hist_pct_error(pct_err: np.ndarray, out_png: Path) -> None:
    fig, ax = plt.subplots(figsize=(6.2, 4.2))
    clipped = np.clip(pct_err, 0.0, 2.0)
    ax.hist(clipped, bins=60, color="#55A868", alpha=0.9)
    ax.set_title("Absolute Percentage Error (Test)")
    ax.set_xlabel("|true - pred| / true (clipped to 2.0)")
    ax.set_ylabel("Count")
    fig.tight_layout()
    fig.savefig(out_png, dpi=200)
    plt.close(fig)


def _scatter_true_abs_error(y_true: np.ndarray, abs_err: np.ndarray, out_png: Path, *, max_points: int = 25000) -> None:
    n = int(y_true.shape[0])
    if n > max_points:
        rng = np.random.default_rng(0)
        sel = rng.choice(n, size=int(max_points), replace=False)
        x = y_true[sel]
        y = abs_err[sel]
    else:
        x = y_true
        y = abs_err

    fig, ax = plt.subplots(figsize=(6.2, 4.6))
    ax.scatter(x, y, s=8, alpha=0.22, color="#C44E52")
    ax.set_xscale("log")
    ax.set_yscale("log")
    ax.set_title("Absolute Error vs True Price (Test)")
    ax.set_xlabel("True price (USD, log)")
    ax.set_ylabel("Absolute error (USD, log)")
    fig.tight_layout()
    fig.savefig(out_png, dpi=200)
    plt.close(fig)


def _plot_bin_metrics(centers: np.ndarray, rmses: np.ndarray, maes: np.ndarray, out_png: Path) -> None:
    fig, ax = plt.subplots(figsize=(7.2, 4.6))
    ax.plot(centers, rmses, marker="o", linewidth=2, label="RMSE")
    ax.plot(centers, maes, marker="o", linewidth=2, label="MAE")
    ax.set_xscale("log")
    ax.set_title("Error vs True-Price Quantile Bins (Test)")
    ax.set_xlabel("Bin center (true price, log)")
    ax.set_ylabel("Error (USD)")
    ax.grid(True, which="both", linestyle="--", alpha=0.35)
    ax.legend()
    fig.tight_layout()
    fig.savefig(out_png, dpi=200)
    plt.close(fig)


def export_error_analysis(*, run_dir: Path, out_dir: Path, tag: str) -> None:
    out_dir.mkdir(parents=True, exist_ok=True)

    _ = _read_json(run_dir / "metrics.json")
    arr = np.load(run_dir / "test_outputs.npz")
    y_true = arr["y_true"].astype(np.float64)
    y_pred = arr["y_pred"].astype(np.float64)

    abs_err = np.abs(y_true - y_pred)
    denom = np.clip(np.abs(y_true), 1.0, None)
    pct_err = abs_err / denom

    out_md = out_dir / f"error_analysis_{tag}.md"
    lines: list[str] = []
    lines.append(f"# Error Analysis — `{tag}`\n")
    lines.append("All numbers are computed on the held-out **test split**.\n")
    lines.append("## Key error stats\n")
    lines.append(f"- Median absolute error: **{float(np.median(abs_err)):.2f}**")
    lines.append(f"- 90th percentile absolute error: **{float(np.quantile(abs_err, 0.90)):.2f}**")
    lines.append(f"- 95th percentile absolute error: **{float(np.quantile(abs_err, 0.95)):.2f}**")
    lines.append(f"- % within $1,000: **{_percent_within(y_true, y_pred, dollars=1000.0) * 100:.2f}%**")
    lines.append(f"- % within $3,000: **{_percent_within(y_true, y_pred, dollars=3000.0) * 100:.2f}%**")
    lines.append(f"- % within 10%: **{_percent_within_pct(y_true, y_pred, pct=0.10) * 100:.2f}%**")
    lines.append(f"- % within 20%: **{_percent_within_pct(y_true, y_pred, pct=0.20) * 100:.2f}%**\n")
    lines.append("## Plots\n")
    lines.append(f"- `error_abs_hist_{tag}.png`")
    lines.append(f"- `error_pct_hist_{tag}.png`")
    lines.append(f"- `error_abs_by_true_{tag}.png`")
    lines.append(f"- `error_by_true_bin_{tag}.png`\n")
    out_md.write_text("\n".join(lines) + "\n", encoding="utf-8")

    _hist_abs_error(abs_err, out_dir / f"error_abs_hist_{tag}.png")
    _hist_pct_error(pct_err, out_dir / f"error_pct_hist_{tag}.png")
    _scatter_true_abs_error(y_true, abs_err, out_dir / f"error_abs_by_true_{tag}.png")

    centers, rmses, maes = _quantile_bin_stats(y_true, y_pred, n_bins=10)
    if centers.size:
        _plot_bin_metrics(centers, rmses, maes, out_dir / f"error_by_true_bin_{tag}.png")


def main() -> int:
    parser = argparse.ArgumentParser()
    parser.add_argument("--run-dir", type=Path, required=True)
    parser.add_argument("--out-dir", type=Path, default=Path("results"))
    parser.add_argument("--tag", type=str, required=True)
    args = parser.parse_args()

    export_error_analysis(run_dir=args.run_dir, out_dir=args.out_dir, tag=args.tag)
    print("Wrote:", args.out_dir / f"error_analysis_{args.tag}.md")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())

