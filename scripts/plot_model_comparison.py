from __future__ import annotations

import argparse
import re
from pathlib import Path

import matplotlib.pyplot as plt
import pandas as pd


def _parse_summary(md: Path) -> dict:
    text = md.read_text(encoding="utf-8", errors="ignore")
    r2_m = re.search(r"(?:R²|R2):\s*\*\*(.+?)\*\*", text)
    rmse_m = re.search(r"RMSE:\s*\*\*(.+?)\*\*", text)
    mae_m = re.search(r"MAE:\s*\*\*(.+?)\*\*", text)
    if not (r2_m and rmse_m and mae_m):
        raise ValueError(f"Failed to parse metrics from {md}")
    r2 = float(r2_m.group(1))
    rmse = float(rmse_m.group(1))
    mae = float(mae_m.group(1))
    model = re.search(r"Model:\\s*`(.+?)`", text)
    model_type = model.group(1) if model else ""
    tag = md.stem.replace("summary_", "")
    return {"tag": tag, "model_type": model_type, "r2": r2, "rmse": rmse, "mae": mae}


def _save(fig, path: Path) -> None:
    path.parent.mkdir(parents=True, exist_ok=True)
    fig.tight_layout()
    fig.savefig(path, dpi=200)
    plt.close(fig)


def main() -> int:
    parser = argparse.ArgumentParser()
    parser.add_argument("--results-dir", type=Path, default=Path("results"))
    parser.add_argument("--out-dir", type=Path, default=Path("results"))
    args = parser.parse_args()

    summaries = sorted(args.results_dir.glob("summary_*.md"))
    rows = [_parse_summary(p) for p in summaries]
    df = pd.DataFrame(rows).sort_values("r2", ascending=False)
    if df.empty:
        raise FileNotFoundError(f"No summary_*.md found under {args.results_dir}")

    out_csv = args.out_dir / "model_comparison.csv"
    df.to_csv(out_csv, index=False)

    # R2 bar
    fig, ax = plt.subplots(figsize=(9.0, 4.6))
    ax.bar(df["tag"], df["r2"], color="#55A868", alpha=0.9)
    ax.axhline(0.8, color="black", linewidth=1.2, linestyle="--", alpha=0.7, label="Target R²=0.80")
    ax.set_title("Model comparison (R² on test)")
    ax.set_xlabel("Experiment tag")
    ax.set_ylabel("R² (higher is better)")
    ax.tick_params(axis="x", rotation=20)
    ax.legend(loc="lower right")
    _save(fig, args.out_dir / "model_comparison_r2.png")

    # RMSE bar (lower better)
    fig, ax = plt.subplots(figsize=(9.0, 4.6))
    ax.bar(df["tag"], df["rmse"], color="#C44E52", alpha=0.9)
    ax.set_title("Model comparison (RMSE on test)")
    ax.set_xlabel("Experiment tag")
    ax.set_ylabel("RMSE (lower is better)")
    ax.tick_params(axis="x", rotation=20)
    _save(fig, args.out_dir / "model_comparison_rmse.png")

    print("Wrote:", out_csv)
    print("Wrote:", args.out_dir / "model_comparison_r2.png")
    print("Wrote:", args.out_dir / "model_comparison_rmse.png")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
