from __future__ import annotations

import argparse
from pathlib import Path

import matplotlib.pyplot as plt


def _box(ax, xy, w, h, text: str) -> None:
    x, y = xy
    rect = plt.Rectangle((x, y), w, h, fill=True, facecolor="#E9F2FB", edgecolor="#2C3E50", linewidth=1.6)
    ax.add_patch(rect)
    ax.text(x + w / 2, y + h / 2, text, ha="center", va="center", fontsize=10)


def _arrow(ax, start, end) -> None:
    ax.annotate(
        "",
        xy=end,
        xytext=start,
        arrowprops=dict(arrowstyle="->", linewidth=1.8, color="#2C3E50"),
    )


def make_pipeline_figure(out_png: Path) -> None:
    out_png.parent.mkdir(parents=True, exist_ok=True)

    fig, ax = plt.subplots(figsize=(12.0, 3.4))
    fig.patch.set_facecolor("white")
    ax.set_axis_off()
    # Use a slightly wider x-range + manual margins to avoid any clipping in
    # different renderers (e.g., GitHub previews).
    ax.set_xlim(0, 1.15)
    ax.set_ylim(0, 1)

    w, h = 0.18, 0.42
    y = 0.28
    xs = [0.04, 0.265, 0.49, 0.715, 0.94]

    _box(ax, (xs[0], y), w, h, "Craigslist\nvehicles.csv")
    _box(ax, (xs[1], y), w, h, "Cleaning\n+ filters\n+ derived feats")
    _box(ax, (xs[2], y), w, h, "Preprocess\n(impute + encode\n+ optional TF-IDF)")
    _box(ax, (xs[3], y), w, h, "Model\n(OLS / Ridge /\nLasso / HGB)")
    _box(ax, (xs[4], y), w, h, "Exports\n(metrics + plots)\n+ Streamlit demo")

    for i in range(4):
        _arrow(ax, (xs[i] + w, y + h / 2), (xs[i + 1], y + h / 2))

    ax.text(
        0.5,
        0.93,
        "DSCI441 Used Car Price Prediction — End-to-End Pipeline",
        ha="center",
        va="center",
        fontsize=12,
        fontweight="bold",
    )

    fig.subplots_adjust(left=0.02, right=0.98, top=0.90, bottom=0.12)
    fig.savefig(out_png, dpi=200, facecolor=fig.get_facecolor())
    plt.close(fig)


def main() -> int:
    parser = argparse.ArgumentParser()
    parser.add_argument("--out", type=Path, default=Path("results/pipeline_overview.png"))
    args = parser.parse_args()
    make_pipeline_figure(args.out)
    print("Wrote:", args.out)
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
