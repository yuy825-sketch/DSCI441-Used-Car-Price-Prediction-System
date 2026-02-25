from __future__ import annotations

import argparse
import json
from pathlib import Path

import matplotlib.pyplot as plt
import numpy as np


def _load_json(path: Path) -> dict:
    with path.open("r", encoding="utf-8") as f:
        return json.load(f)


def _write_summary(metrics: dict, out_md: Path) -> None:
    out_md.parent.mkdir(parents=True, exist_ok=True)
    test = metrics["test"]

    lines: list[str] = []
    lines.append("# Results Summary\n")
    lines.append("## Key metrics (test)\n")
    lines.append(f"- R²: **{test['r2']:.4f}**")
    lines.append(f"- RMSE: **{test['rmse']:.2f}**")
    lines.append(f"- MAE: **{test['mae']:.2f}**\n")
    lines.append("## Notes\n")
    lines.append(f"- Model: `{metrics['config']['model_type']}`")
    lines.append(f"- Log target: `{metrics['config']['log_target']}`")
    lines.append(f"- Rows used (after cleaning): `{metrics['config']['n_rows']}`")
    out_md.write_text("\n".join(lines) + "\n", encoding="utf-8")


def _scatter_true_pred(y_true: np.ndarray, y_pred: np.ndarray, out_png: Path) -> None:
    out_png.parent.mkdir(parents=True, exist_ok=True)
    fig, ax = plt.subplots(figsize=(6.2, 6.2))
    ax.scatter(y_true, y_pred, s=8, alpha=0.25)
    mn = float(min(y_true.min(), y_pred.min()))
    mx = float(max(y_true.max(), y_pred.max()))
    ax.plot([mn, mx], [mn, mx], color="black", linewidth=1.2, alpha=0.8)
    ax.set_xlabel("True price")
    ax.set_ylabel("Predicted price")
    ax.set_title("True vs Predicted (Test)")
    fig.tight_layout()
    fig.savefig(out_png, dpi=200)
    plt.close(fig)


def _residual_plots(y_true: np.ndarray, y_pred: np.ndarray, out_dir: Path, *, suffix: str) -> None:
    out_dir.mkdir(parents=True, exist_ok=True)
    resid = y_true - y_pred

    fig, ax = plt.subplots(figsize=(6.2, 4.2))
    ax.hist(resid, bins=50, color="#4C72B0", alpha=0.85)
    ax.set_title("Residual Histogram (Test)")
    ax.set_xlabel("Residual (true - pred)")
    ax.set_ylabel("Count")
    fig.tight_layout()
    fig.savefig(out_dir / f"residuals_hist{suffix}.png", dpi=200)
    plt.close(fig)

    fig, ax = plt.subplots(figsize=(6.2, 4.2))
    ax.scatter(y_pred, resid, s=8, alpha=0.25)
    ax.axhline(0.0, color="black", linewidth=1.0, alpha=0.7)
    ax.set_title("Residuals vs Predicted (Test)")
    ax.set_xlabel("Predicted price")
    ax.set_ylabel("Residual (true - pred)")
    fig.tight_layout()
    fig.savefig(out_dir / f"residuals_scatter{suffix}.png", dpi=200)
    plt.close(fig)


def _top_coeffs(coeffs: dict, out_png: Path, k: int = 25) -> None:
    coef = np.asarray(coeffs.get("coef", []), dtype=np.float64)
    names = list(coeffs.get("feature_names_out", []))
    if coef.size == 0 or len(names) != coef.size:
        return

    idx = np.argsort(np.abs(coef))[-int(k) :]
    idx = idx[np.argsort(np.abs(coef[idx]))]
    sel_coef = coef[idx]
    sel_names = [names[i] for i in idx]

    out_png.parent.mkdir(parents=True, exist_ok=True)
    fig, ax = plt.subplots(figsize=(8.5, 6.5))
    ax.barh(sel_names, sel_coef, color=["#C44E52" if c < 0 else "#55A868" for c in sel_coef])
    ax.set_title(f"Top {len(sel_coef)} coefficients (by |value|)")
    ax.set_xlabel("Coefficient")
    fig.tight_layout()
    fig.savefig(out_png, dpi=200)
    plt.close(fig)


def export_run(*, run_dir: Path, out_dir: Path, tag: str | None = None) -> None:
    metrics = _load_json(run_dir / "metrics.json")
    arr = np.load(run_dir / "test_outputs.npz")
    y_true = arr["y_true"].astype(np.float64)
    y_pred = arr["y_pred"].astype(np.float64)

    suffix = f"_{tag}" if tag else ""
    _write_summary(metrics, out_dir / f"summary{suffix}.md")
    _scatter_true_pred(y_true, y_pred, out_dir / f"true_vs_pred{suffix}.png")
    _residual_plots(y_true, y_pred, out_dir, suffix=suffix)

    coef_path = run_dir / "coefficients.json"
    if coef_path.exists():
        coeffs = _load_json(coef_path)
        _top_coeffs(coeffs, out_dir / f"top_coeffs{suffix}.png")


def main() -> int:
    parser = argparse.ArgumentParser()
    parser.add_argument("--run-dir", type=Path, required=True, help="Path to a run folder containing metrics.json")
    parser.add_argument("--out-dir", type=Path, default=Path("results"))
    parser.add_argument("--tag", type=str, default=None, help="Optional suffix for output filenames")
    args = parser.parse_args()

    export_run(run_dir=args.run_dir, out_dir=args.out_dir, tag=args.tag)
    suffix = f"_{args.tag}" if args.tag else ""
    print("Wrote:", args.out_dir / f"summary{suffix}.md")
    print("Wrote:", args.out_dir / f"true_vs_pred{suffix}.png")
    print("Wrote:", args.out_dir / f"residuals_hist{suffix}.png")
    print("Wrote:", args.out_dir / f"residuals_scatter{suffix}.png")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
