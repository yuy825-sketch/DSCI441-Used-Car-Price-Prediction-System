from __future__ import annotations

import json
import os
import shutil
import subprocess
from pathlib import Path


def _have_kaggle_creds() -> bool:
    if os.getenv("KAGGLE_USERNAME") and os.getenv("KAGGLE_KEY"):
        return True
    return (Path.home() / ".kaggle" / "kaggle.json").exists()


def _ensure_kaggle_cli() -> None:
    if shutil.which("kaggle") is not None:
        return
    raise RuntimeError(
        "Missing `kaggle` CLI. Install it in your environment:\n"
        "  pip install kaggle\n"
        "Then re-run this script."
    )


def main() -> int:
    out_dir = Path("data/craigslist")
    out_dir.mkdir(parents=True, exist_ok=True)

    expected = out_dir / "vehicles.csv"
    if expected.exists():
        print("OK: dataset already exists:", expected)
        return 0

    if not _have_kaggle_creds():
        msg = (
            "Kaggle API credentials not found.\n\n"
            "Option A (recommended): create ~/.kaggle/kaggle.json with:\n"
            '  {"username":"<your_username>","key":"<your_key>"}\n'
            "and run: chmod 600 ~/.kaggle/kaggle.json\n\n"
            "Option B: set env vars:\n"
            "  export KAGGLE_USERNAME='<your_username>'\n"
            "  export KAGGLE_KEY='<your_key>'\n\n"
            "Then re-run:\n"
            "  python scripts/download_kaggle_dataset.py\n"
        )
        raise RuntimeError(msg)

    _ensure_kaggle_cli()

    dataset = os.getenv("DSCI441_KAGGLE_DATASET", "austinreese/craigslist-carstrucks-data")
    print("Downloading Kaggle dataset:", dataset)
    subprocess.check_call(
        [
            "kaggle",
            "datasets",
            "download",
            "-d",
            dataset,
            "-p",
            str(out_dir),
            "--unzip",
        ]
    )

    # Some Kaggle mirrors may use different filenames.
    if expected.exists():
        print("OK: wrote", expected)
        return 0

    candidates = list(out_dir.glob("*.csv"))
    if len(candidates) == 1:
        candidates[0].rename(expected)
        print("OK: renamed", candidates[0].name, "->", expected)
        return 0

    raise FileNotFoundError(f"Download finished, but {expected} not found. CSV files in {out_dir}: {candidates}")


if __name__ == "__main__":
    raise SystemExit(main())

