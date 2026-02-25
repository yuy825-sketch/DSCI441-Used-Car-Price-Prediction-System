from __future__ import annotations

import os
import shutil
import subprocess
from pathlib import Path
import time


def _load_token_from_file() -> str | None:
    candidates = [
        Path.home() / ".kaggle" / "kaggle_api_token",
        Path.home() / ".kaggle" / "api_token",
    ]
    for p in candidates:
        if p.exists():
            token = p.read_text(encoding="utf-8", errors="ignore").strip()
            if token:
                return token
    return None


def _have_kaggle_creds() -> bool:
    if os.getenv("KAGGLE_API_TOKEN"):
        return True
    if _load_token_from_file() is not None:
        return True
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


def _parse_total_bytes_from_content_range(hdr: str) -> int | None:
    # Example: "bytes 0-1023/123456"
    try:
        if "/" not in hdr:
            return None
        total_str = hdr.split("/", 1)[1].strip()
        if total_str.isdigit():
            return int(total_str)
        return None
    except Exception:
        return None


def _download_url_to_zip(*, url: str, zip_path: Path) -> None:
    import requests

    zip_path.parent.mkdir(parents=True, exist_ok=True)
    part_path = zip_path.with_suffix(zip_path.suffix + ".part")
    existing = part_path.stat().st_size if part_path.exists() else 0

    headers = {}
    if existing > 0:
        headers["Range"] = f"bytes={existing}-"

    resp = requests.get(url, stream=True, headers=headers, timeout=(30, 60))
    if resp.status_code == 206:
        mode = "ab"
        total = _parse_total_bytes_from_content_range(resp.headers.get("Content-Range", ""))  # type: ignore[arg-type]
    elif resp.status_code == 200:
        mode = "wb"
        existing = 0
        total = int(resp.headers.get("Content-Length", "0") or "0") or None
    else:
        resp.raise_for_status()
        raise RuntimeError("Unreachable")

    downloaded = existing
    last_print = time.time()
    t0 = last_print
    with part_path.open(mode) as f:
        for chunk in resp.iter_content(chunk_size=1024 * 1024):
            if not chunk:
                continue
            f.write(chunk)
            downloaded += len(chunk)
            now = time.time()
            if now - last_print >= 5.0:
                rate = (downloaded - existing) / max(1e-6, now - t0)
                if total:
                    pct = 100.0 * downloaded / total
                    print(f"Downloaded: {downloaded/1e6:.1f}MB / {total/1e6:.1f}MB ({pct:.1f}%) @ {rate/1e6:.2f}MB/s")
                else:
                    print(f"Downloaded: {downloaded/1e6:.1f}MB @ {rate/1e6:.2f}MB/s")
                last_print = now

    # If server provided a total, require completion before renaming.
    if total is not None:
        final_size = part_path.stat().st_size
        if final_size != total:
            raise RuntimeError(
                f"Download incomplete (got {final_size} bytes, expected {total}). Re-run to resume: {part_path}"
            )

    part_path.replace(zip_path)


def _download_with_kagglesdk(*, dataset: str, out_dir: Path) -> None:
    token = os.getenv("KAGGLE_API_TOKEN") or _load_token_from_file()
    if not token:
        raise RuntimeError("KAGGLE_API_TOKEN not found (env var or ~/.kaggle/kaggle_api_token).")

    from kagglesdk.kaggle_client import KaggleClient
    from kagglesdk.datasets.types.dataset_api_service import ApiDownloadDatasetRequest

    if "/" not in dataset:
        raise ValueError(f"Invalid dataset id: {dataset} (expected owner_slug/dataset_slug)")
    owner_slug, dataset_slug = dataset.split("/", 1)

    client = KaggleClient(api_token=token, user_agent="dsci441-used-car/0.1.0")
    req = ApiDownloadDatasetRequest()
    req.owner_slug = owner_slug
    req.dataset_slug = dataset_slug
    req.raw = False

    resp = client.datasets.dataset_api_client.download_dataset(req)

    # `resp` is a `requests.Response` (see kagglesdk.common.types.http_redirect.HttpRedirect.prepare_from).
    if not hasattr(resp, "status_code"):
        raise RuntimeError("Unexpected Kaggle response type (expected requests.Response).")

    out_dir.mkdir(parents=True, exist_ok=True)
    zip_path = out_dir / "kaggle_dataset.zip"

    status = int(resp.status_code)
    if status in {301, 302, 303, 307, 308} and resp.headers.get("Location"):
        url = resp.headers["Location"]
        print("Following redirect to signed download URL...")
        _download_url_to_zip(url=url, zip_path=zip_path)
    else:
        # Fallback: treat response body as the zip payload.
        with zip_path.open("wb") as f:
            for chunk in resp.iter_content(chunk_size=1024 * 1024):
                if chunk:
                    f.write(chunk)

    import zipfile

    with zipfile.ZipFile(zip_path, "r") as z:
        z.extractall(out_dir)

    try:
        zip_path.unlink()
    except Exception:
        pass


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
            "Option A (token, preferred): set env var `KAGGLE_API_TOKEN` OR write it to:\n"
            "  ~/.kaggle/kaggle_api_token\n"
            "and run: chmod 600 ~/.kaggle/kaggle_api_token\n\n"
            "Option B (legacy): create ~/.kaggle/kaggle.json with:\n"
            '  {"username":"<your_username>","key":"<your_key>"}\n'
            "and run: chmod 600 ~/.kaggle/kaggle.json\n\n"
            "Option C (legacy env vars):\n"
            "  export KAGGLE_USERNAME='<your_username>'\n"
            "  export KAGGLE_KEY='<your_key>'\n\n"
            "Then re-run:\n"
            "  python scripts/download_kaggle_dataset.py\n"
        )
        raise RuntimeError(msg)

    dataset = os.getenv("DSCI441_KAGGLE_DATASET", "austinreese/craigslist-carstrucks-data")
    print("Downloading Kaggle dataset:", dataset)
    used_sdk = False
    if os.getenv("KAGGLE_API_TOKEN") or _load_token_from_file() is not None:
        _download_with_kagglesdk(dataset=dataset, out_dir=out_dir)
        used_sdk = True
    else:
        _ensure_kaggle_cli()
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
        print("Auth mode:", "kagglesdk (token)" if used_sdk else "kaggle CLI (username/key)")
        return 0

    candidates = list(out_dir.glob("*.csv"))
    if len(candidates) == 1:
        candidates[0].rename(expected)
        print("OK: renamed", candidates[0].name, "->", expected)
        print("Auth mode:", "kagglesdk (token)" if used_sdk else "kaggle CLI (username/key)")
        return 0

    raise FileNotFoundError(f"Download finished, but {expected} not found. CSV files in {out_dir}: {candidates}")


if __name__ == "__main__":
    raise SystemExit(main())
