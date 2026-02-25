from __future__ import annotations

import json
import subprocess
import sys
from pathlib import Path


SKILL_EDA = Path("/home/shuaijun/.codex/skills/data-quality-eda-results/scripts/eda_analyzer.py")
SKILL_AGG = Path("/home/shuaijun/.codex/skills/data-quality-eda-results/scripts/aggregate_results.py")


def _run(cmd: list[str]) -> None:
    print("+", " ".join(cmd))
    subprocess.check_call(cmd)


def _find_latest_run_dir(runs_root: Path) -> Path:
    candidates = [p for p in runs_root.iterdir() if p.is_dir() and (p / "metrics.json").exists()]
    if not candidates:
        raise FileNotFoundError(f"No completed runs found under {runs_root}")
    return sorted(candidates)[-1]


def main() -> int:
    repo_root = Path(__file__).resolve().parents[1]
    dataset = repo_root / "data" / "craigslist" / "vehicles.csv"
    if not dataset.exists():
        raise FileNotFoundError(
            f"Dataset not found: {dataset}\n"
            "Run:\n"
            "  python scripts/download_kaggle_dataset.py\n"
            "or place the CSV manually under data/craigslist/vehicles.csv"
        )

    # 1) QC/EDA (sample-based)
    (repo_root / "project" / "data_qc").mkdir(parents=True, exist_ok=True)
    _run([sys.executable, str(SKILL_EDA), str(dataset), str(repo_root / "project" / "data_qc" / "vehicles_eda.md")])

    # 2) Baseline training runs
    experiments = [
        ("ols", repo_root / "configs" / "baseline_ols.json"),
        ("ridge", repo_root / "configs" / "ridge.json"),
        ("lasso", repo_root / "configs" / "lasso.json"),
        ("ridge_text_a20", repo_root / "configs" / "ridge_text_alpha20.json"),
        ("hgb_ordinal", repo_root / "configs" / "hgb_ordinal.json"),
    ]

    runs_root = repo_root / "runs"
    for tag, cfg in experiments:
        _run([sys.executable, str(repo_root / "train.py"), "--config", str(cfg), "--run-name", tag])
        latest = _find_latest_run_dir(runs_root)
        _run(
            [
                sys.executable,
                str(repo_root / "scripts" / "export_results.py"),
                "--run-dir",
                str(latest),
                "--out-dir",
                str(repo_root / "results"),
                "--tag",
                tag,
            ]
        )

    # 3) Aggregate into a table (paper/report friendly)
    out_dir = repo_root / "project" / "results"
    out_dir.mkdir(parents=True, exist_ok=True)
    _run(
        [
            sys.executable,
            str(SKILL_AGG),
            "--inputs",
            str(repo_root / "runs"),
            str(repo_root / "results"),
            "--out-md",
            str(out_dir / "results_table.md"),
            "--out-csv",
            str(out_dir / "results_table.csv"),
            "--schema-out",
            str(out_dir / "results_schema.json"),
        ]
    )

    print("OK: completed baselines and exports.")
    print("Report:", repo_root / "results" / "REPORT.md")
    print("Results table:", out_dir / "results_table.md")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
