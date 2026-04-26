from __future__ import annotations

import argparse
import json
from pathlib import Path

import joblib
import matplotlib.pyplot as plt
import numpy as np
import pandas as pd
from sklearn.model_selection import train_test_split

from dsci441_used_car.data import CleanSpec, clean_dataset, load_vehicles_csv


def _read_json(path: Path) -> dict:
    with path.open("r", encoding="utf-8") as f:
        return json.load(f)


def _resolve_path(path_like: str, *, repo_root: Path) -> Path:
    p = Path(path_like)
    if p.is_absolute():
        return p
    return repo_root / p


def _prepare_eval_frame(*, run_dir: Path, repo_root: Path) -> pd.DataFrame:
    cfg = _read_json(run_dir / "config.json")
    ds = cfg["dataset"]

    csv_path = _resolve_path(str(ds["path"]), repo_root=repo_root)
    spec = CleanSpec(
        min_price=float(ds.get("min_price", 100)),
        max_price=float(ds.get("max_price", 200000)),
        min_year=int(ds.get("min_year", 1970)),
        max_year=int(ds.get("max_year", 2026)),
        max_odometer=float(ds.get("max_odometer", 500000)),
    )

    target = str(ds.get("target", "price"))
    features = list(ds["features"])
    df_raw = load_vehicles_csv(csv_path, sample_n=ds.get("sample_n", None))
    df = clean_dataset(df_raw, target=target, features=features, spec=spec)

    if "car_age" in df.columns and "car_age" not in features:
        features = [*features, "car_age"]
    if "miles_per_year" in df.columns and "miles_per_year" not in features:
        features = [*features, "miles_per_year"]

    X = df[features]
    y = df[target].to_numpy(dtype=np.float64)

    split_cfg = cfg.get("split", {})
    test_size = float(split_cfg.get("test_size", 0.2))
    seed = int(split_cfg.get("seed", 441))
    _, X_test, _, y_test = train_test_split(X, y, test_size=test_size, random_state=seed)

    model = joblib.load(run_dir / "model.joblib")
    y_pred = model.predict(X_test)

    out = X_test.reset_index(drop=True).copy()
    out["y_true"] = y_test.astype(np.float64)
    out["y_pred"] = np.asarray(y_pred, dtype=np.float64)
    out["residual"] = out["y_true"] - out["y_pred"]
    out["abs_error"] = np.abs(out["residual"])
    denom = np.clip(np.abs(out["y_true"].to_numpy(dtype=np.float64)), 1.0, None)
    out["ape"] = out["abs_error"] / denom

    for c in ["condition", "fuel", "manufacturer", "type"]:
        if c in out.columns:
            out[c] = out[c].astype("string").fillna("missing").replace({"": "missing"})
    return out


def _plot_mae_by_category(df: pd.DataFrame, *, col: str, out_png: Path, title: str, top_n: int = 10, min_count: int = 120) -> pd.DataFrame:
    g = (
        df.groupby(col, dropna=False)
        .agg(n=("abs_error", "size"), mae=("abs_error", "mean"), mape=("ape", "mean"), bias=("residual", "mean"))
        .sort_values("n", ascending=False)
    )
    g = g[g["n"] >= int(min_count)].head(int(top_n)).sort_values("mae", ascending=True)
    if g.empty:
        return g

    fig, ax = plt.subplots(figsize=(8.6, 4.8))
    bars = ax.barh(g.index.astype(str), g["mae"], color="#2f7fbf", alpha=0.9)
    for b, n in zip(bars, g["n"].to_numpy()):
        ax.text(float(b.get_width()) + 40, b.get_y() + b.get_height() * 0.5, f"n={int(n)}", va="center", fontsize=9, color="#45525a")
    ax.set_title(title)
    ax.set_xlabel("Mean absolute error (USD)")
    ax.set_ylabel(col)
    ax.grid(axis="x", linestyle="--", alpha=0.3)
    fig.tight_layout()
    fig.savefig(out_png, dpi=220)
    plt.close(fig)
    return g


def _plot_bias_and_mae_by_price_decile(df: pd.DataFrame, *, out_png: Path) -> pd.DataFrame:
    b = df.copy()
    b["price_decile"] = pd.qcut(b["y_true"], q=10, duplicates="drop")
    stat = (
        b.groupby("price_decile", observed=False)
        .agg(n=("abs_error", "size"), true_mid=("y_true", "median"), mae=("abs_error", "mean"), bias=("residual", "mean"))
        .reset_index(drop=True)
    )
    if stat.empty:
        return stat

    x = np.arange(len(stat))
    fig, ax1 = plt.subplots(figsize=(8.8, 4.8))
    ax1.bar(x, stat["mae"], color="#4b8d74", alpha=0.85, label="MAE")
    ax1.set_xlabel("True-price decile (low -> high)")
    ax1.set_ylabel("MAE (USD)")
    ax1.set_xticks(x)
    ax1.set_xticklabels([f"D{i+1}" for i in x], fontsize=9)
    ax1.grid(axis="y", linestyle="--", alpha=0.3)

    ax2 = ax1.twinx()
    ax2.plot(x, stat["bias"], marker="o", color="#b84f3f", linewidth=2.0, label="Mean residual")
    ax2.axhline(0.0, color="#2f3133", linewidth=1.0, alpha=0.6)
    ax2.set_ylabel("Mean residual (USD)")
    ax1.set_title("Error profile by true-price decile")

    l1, n1 = ax1.get_legend_handles_labels()
    l2, n2 = ax2.get_legend_handles_labels()
    ax1.legend(l1 + l2, n1 + n2, loc="upper left")
    fig.tight_layout()
    fig.savefig(out_png, dpi=220)
    plt.close(fig)
    return stat


def _plot_calibration_pred_vs_true(df: pd.DataFrame, *, out_png: Path) -> pd.DataFrame:
    b = df.copy()
    b["pred_decile"] = pd.qcut(b["y_pred"], q=10, duplicates="drop")
    stat = (
        b.groupby("pred_decile", observed=False)
        .agg(n=("y_pred", "size"), pred_mean=("y_pred", "mean"), true_mean=("y_true", "mean"), mae=("abs_error", "mean"))
        .reset_index(drop=True)
    )
    if stat.empty:
        return stat

    lo = float(min(stat["pred_mean"].min(), stat["true_mean"].min()))
    hi = float(max(stat["pred_mean"].max(), stat["true_mean"].max()))

    fig, ax = plt.subplots(figsize=(6.6, 6.2))
    ax.plot([lo, hi], [lo, hi], color="#2f3133", linewidth=1.2, linestyle="--", label="Ideal: pred = true")
    sc = ax.scatter(stat["pred_mean"], stat["true_mean"], c=stat["mae"], cmap="viridis", s=90, edgecolors="black", linewidths=0.3)
    for i, (xp, yp) in enumerate(zip(stat["pred_mean"], stat["true_mean"])):
        ax.text(float(xp), float(yp), f" D{i+1}", fontsize=9, color="#1f2529", va="center")
    cbar = fig.colorbar(sc, ax=ax, shrink=0.86)
    cbar.set_label("MAE in bin (USD)")
    ax.set_xlabel("Mean predicted price by prediction decile")
    ax.set_ylabel("Mean true price in same decile")
    ax.set_title("Prediction-decile calibration view")
    ax.legend(loc="upper left")
    fig.tight_layout()
    fig.savefig(out_png, dpi=220)
    plt.close(fig)
    return stat


def _plot_mae_heatmap_condition_fuel(df: pd.DataFrame, *, out_png: Path, min_count: int = 80) -> pd.DataFrame:
    temp = df.copy()
    cond_top = temp["condition"].value_counts().head(6).index.tolist()
    fuel_top = temp["fuel"].value_counts().head(6).index.tolist()
    temp = temp[temp["condition"].isin(cond_top) & temp["fuel"].isin(fuel_top)]

    grp = temp.groupby(["condition", "fuel"]).agg(n=("abs_error", "size"), mae=("abs_error", "mean")).reset_index()
    grp = grp[grp["n"] >= int(min_count)]
    if grp.empty:
        return grp

    pv = grp.pivot(index="condition", columns="fuel", values="mae").sort_index(axis=0).sort_index(axis=1)
    fig, ax = plt.subplots(figsize=(7.2, 5.4))
    m = ax.imshow(pv.to_numpy(dtype=np.float64), cmap="YlOrRd", aspect="auto")
    fig.colorbar(m, ax=ax, shrink=0.84, label="MAE (USD)")
    ax.set_xticks(np.arange(len(pv.columns)))
    ax.set_xticklabels([str(c) for c in pv.columns], rotation=30, ha="right")
    ax.set_yticks(np.arange(len(pv.index)))
    ax.set_yticklabels([str(i) for i in pv.index])
    ax.set_title("MAE heatmap by condition x fuel")

    arr = pv.to_numpy(dtype=np.float64)
    for i in range(arr.shape[0]):
        for j in range(arr.shape[1]):
            val = arr[i, j]
            if np.isnan(val):
                continue
            ax.text(j, i, f"{val:.0f}", ha="center", va="center", fontsize=8, color="#1f2529")

    fig.tight_layout()
    fig.savefig(out_png, dpi=220)
    plt.close(fig)
    return grp


def _plot_age_bucket_errors(df: pd.DataFrame, *, out_png: Path) -> pd.DataFrame:
    if "car_age" not in df.columns:
        return pd.DataFrame()

    temp = df.copy()
    age = pd.to_numeric(temp["car_age"], errors="coerce")
    bins = [-1, 4, 9, 14, 24, 100]
    labels = ["0-4", "5-9", "10-14", "15-24", "25+"]
    temp["age_bucket"] = pd.cut(age, bins=bins, labels=labels)
    stat = temp.groupby("age_bucket", observed=False).agg(n=("abs_error", "size"), mae=("abs_error", "mean"), mape=("ape", "mean")).reset_index()
    stat = stat[stat["n"] > 0]
    if stat.empty:
        return stat

    x = np.arange(len(stat))
    fig, ax1 = plt.subplots(figsize=(7.6, 4.8))
    ax1.bar(x, stat["mae"], color="#3a79a8", alpha=0.9, label="MAE (USD)")
    ax1.set_xticks(x)
    ax1.set_xticklabels(stat["age_bucket"].astype(str))
    ax1.set_ylabel("MAE (USD)")
    ax1.set_xlabel("Vehicle age bucket (years)")
    ax1.grid(axis="y", linestyle="--", alpha=0.25)

    ax2 = ax1.twinx()
    ax2.plot(x, stat["mape"] * 100.0, color="#c05e41", marker="o", linewidth=2.0, label="MAPE (%)")
    ax2.set_ylabel("MAPE (%)")
    ax1.set_title("Error by vehicle-age bucket")

    l1, n1 = ax1.get_legend_handles_labels()
    l2, n2 = ax2.get_legend_handles_labels()
    ax1.legend(l1 + l2, n1 + n2, loc="upper left")
    fig.tight_layout()
    fig.savefig(out_png, dpi=220)
    plt.close(fig)
    return stat


def _write_summary(
    *,
    out_md: Path,
    run_dir: Path,
    n_test: int,
    stat_condition: pd.DataFrame,
    stat_fuel: pd.DataFrame,
    stat_decile: pd.DataFrame,
    stat_cal: pd.DataFrame,
) -> None:
    lines: list[str] = []
    lines.append("# Advanced Diagnostics (DSCI441 Extension)\n")
    lines.append(f"- Source run: `{run_dir}`")
    lines.append(f"- Test samples analyzed: **{n_test:,}**\n")
    lines.append("## New figures")
    lines.append("- `mae_by_condition_hgb_ordinal.png`")
    lines.append("- `mae_by_fuel_hgb_ordinal.png`")
    lines.append("- `bias_by_price_decile_hgb_ordinal.png`")
    lines.append("- `calibration_pred_vs_true_decile_hgb_ordinal.png`")
    lines.append("- `mae_heatmap_condition_fuel_hgb_ordinal.png`")
    lines.append("- `error_by_age_bucket_hgb_ordinal.png`\n")

    if not stat_condition.empty:
        top = stat_condition.sort_values("mae", ascending=False).iloc[0]
        lines.append("## Condition subgroup note")
        lines.append(f"- Highest MAE subgroup in plotted condition set: `{top.name}` with MAE **{top['mae']:.1f} USD**.")
    if not stat_fuel.empty:
        top = stat_fuel.sort_values("mae", ascending=False).iloc[0]
        lines.append("## Fuel subgroup note")
        lines.append(f"- Highest MAE subgroup in plotted fuel set: `{top.name}` with MAE **{top['mae']:.1f} USD**.")
    if not stat_decile.empty:
        d10 = stat_decile.iloc[-1]
        d1 = stat_decile.iloc[0]
        lines.append("## Price-scale behavior")
        lines.append(f"- MAE increases from **{d1['mae']:.1f} USD** (lowest decile) to **{d10['mae']:.1f} USD** (highest decile).")
    if not stat_cal.empty:
        gap = float(np.mean(np.abs(stat_cal["pred_mean"] - stat_cal["true_mean"])))
        lines.append("## Decile calibration gap")
        lines.append(f"- Mean absolute gap between decile-level predicted and true mean prices: **{gap:.1f} USD**.")

    lines.append("\n## Interpretation")
    lines.append("- The best broad-domain model remains strong, but absolute-dollar error is not uniform across market segments.")
    lines.append("- Segment-aware monitoring (condition/fuel/age) helps explain where residual risk is concentrated.")
    lines.append("- Decile calibration and bias-by-price plots provide deployment-facing diagnostics beyond global RMSE/R².")
    out_md.write_text("\n".join(lines) + "\n", encoding="utf-8")


def export_advanced(*, run_dir: Path, out_dir: Path, tag: str) -> None:
    out_dir.mkdir(parents=True, exist_ok=True)
    repo_root = Path(__file__).resolve().parents[1]
    df = _prepare_eval_frame(run_dir=run_dir, repo_root=repo_root)

    stat_condition = _plot_mae_by_category(
        df,
        col="condition",
        out_png=out_dir / f"mae_by_condition_{tag}.png",
        title="MAE by condition subgroup",
        top_n=8,
        min_count=120,
    )
    stat_fuel = _plot_mae_by_category(
        df,
        col="fuel",
        out_png=out_dir / f"mae_by_fuel_{tag}.png",
        title="MAE by fuel subgroup",
        top_n=8,
        min_count=120,
    )
    stat_decile = _plot_bias_and_mae_by_price_decile(df, out_png=out_dir / f"bias_by_price_decile_{tag}.png")
    stat_cal = _plot_calibration_pred_vs_true(df, out_png=out_dir / f"calibration_pred_vs_true_decile_{tag}.png")
    _ = _plot_mae_heatmap_condition_fuel(df, out_png=out_dir / f"mae_heatmap_condition_fuel_{tag}.png", min_count=80)
    _ = _plot_age_bucket_errors(df, out_png=out_dir / f"error_by_age_bucket_{tag}.png")

    _write_summary(
        out_md=out_dir / "README.md",
        run_dir=run_dir,
        n_test=int(df.shape[0]),
        stat_condition=stat_condition,
        stat_fuel=stat_fuel,
        stat_decile=stat_decile,
        stat_cal=stat_cal,
    )


def main() -> int:
    parser = argparse.ArgumentParser()
    parser.add_argument("--run-dir", type=Path, required=True, help="Run directory containing model.joblib and config.json")
    parser.add_argument("--out-dir", type=Path, default=Path("results/advanced"))
    parser.add_argument("--tag", type=str, default="hgb_ordinal")
    args = parser.parse_args()

    export_advanced(run_dir=args.run_dir, out_dir=args.out_dir, tag=args.tag)
    print("Wrote advanced diagnostics to:", args.out_dir)
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
