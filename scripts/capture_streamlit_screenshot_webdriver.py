from __future__ import annotations

import argparse
import base64
import json
import os
import subprocess
import sys
import time
import urllib.error
import urllib.request
from pathlib import Path


def _http_json(method: str, url: str, payload: dict | None = None) -> dict:
    data = None
    headers = {"Content-Type": "application/json; charset=utf-8"}
    if payload is not None:
        data = json.dumps(payload).encode("utf-8")
    req = urllib.request.Request(url, data=data, headers=headers, method=method)
    with urllib.request.urlopen(req, timeout=10) as resp:
        raw = resp.read()
    return json.loads(raw.decode("utf-8"))


def _wait_http_ok(url: str, *, timeout_s: int = 40) -> None:
    start = time.time()
    while True:
        try:
            with urllib.request.urlopen(url, timeout=2) as resp:
                if resp.status < 500:
                    return
        except Exception:
            pass
        if time.time() - start > timeout_s:
            raise TimeoutError(f"Timed out waiting for {url}")
        time.sleep(1)


def _webdriver_value(resp: dict) -> object:
    # W3C WebDriver responses often contain {"value": ...}
    if isinstance(resp, dict) and "value" in resp:
        return resp["value"]
    return resp


def _ensure_dir(path: Path) -> None:
    path.parent.mkdir(parents=True, exist_ok=True)


def capture_screenshot(
    *,
    app_url: str,
    out_png: Path,
    geckodriver_url: str = "http://127.0.0.1:4444",
    wait_ready_contains: str = "Enter vehicle details",
    wait_timeout_s: int = 60,
    width: int = 1400,
    height: int = 900,
) -> None:
    # Create session (headless Firefox).
    create = _http_json(
        "POST",
        f"{geckodriver_url}/session",
        {
            "capabilities": {
                "alwaysMatch": {
                    "browserName": "firefox",
                    "moz:firefoxOptions": {"args": ["-headless"]},
                    "pageLoadStrategy": "normal",
                }
            }
        },
    )
    session_id = str(_webdriver_value(create).get("sessionId") or create.get("sessionId"))
    if not session_id:
        raise RuntimeError(f"Failed to create session: {create}")

    try:
        _http_json("POST", f"{geckodriver_url}/session/{session_id}/url", {"url": app_url})

        # Set viewport.
        try:
            _http_json(
                "POST",
                f"{geckodriver_url}/session/{session_id}/window/rect",
                {"width": int(width), "height": int(height)},
            )
        except Exception:
            pass

        # Poll until Streamlit has rendered key UI text (JS-rendered), then screenshot.
        start = time.time()
        while True:
            try:
                r = _http_json(
                    "POST",
                    f"{geckodriver_url}/session/{session_id}/execute/sync",
                    {
                        "script": "return (document.body && document.body.innerText) || '';",
                        "args": [],
                    },
                )
                body_text = str(_webdriver_value(r) or "")
                if wait_ready_contains in body_text and "Running _load_model" not in body_text:
                    break
            except urllib.error.URLError:
                pass

            if time.time() - start > float(wait_timeout_s):
                break
            time.sleep(1)

        shot = _http_json("GET", f"{geckodriver_url}/session/{session_id}/screenshot")
        b64 = str(_webdriver_value(shot) or "")
        if not b64:
            raise RuntimeError(f"Empty screenshot response: {shot}")

        _ensure_dir(out_png)
        out_png.write_bytes(base64.b64decode(b64.encode("utf-8")))
    finally:
        try:
            _http_json("DELETE", f"{geckodriver_url}/session/{session_id}")
        except Exception:
            pass


def main() -> int:
    parser = argparse.ArgumentParser()
    parser.add_argument("--out", type=Path, default=Path("results/streamlit_demo.png"))
    parser.add_argument("--port", type=int, default=8501)
    parser.add_argument("--addr", type=str, default="127.0.0.1")
    parser.add_argument("--wait-ready", type=str, default="Enter vehicle details")
    parser.add_argument("--wait-timeout", type=int, default=60)
    parser.add_argument("--width", type=int, default=1400)
    parser.add_argument("--height", type=int, default=900)
    args = parser.parse_args()

    repo_root = Path(__file__).resolve().parents[1]
    app_url = f"http://{args.addr}:{int(args.port)}"

    # Start Streamlit (headless) in background.
    default_run_dir = repo_root / "runs" / "20260225_155344__hgb-ordinal"
    os.environ.setdefault("DSCI441_DEMO_RUN_DIR", str(default_run_dir))

    streamlit_cmd = [
        sys.executable,
        "-m",
        "streamlit",
        "run",
        str(repo_root / "app" / "app.py"),
        "--server.headless",
        "true",
        "--server.address",
        args.addr,
        "--server.port",
        str(int(args.port)),
    ]

    log_path = Path("/tmp/dsci441_streamlit.log")
    with log_path.open("wb") as logf:
        proc = subprocess.Popen(streamlit_cmd, stdout=logf, stderr=subprocess.STDOUT)

    try:
        _wait_http_ok(app_url, timeout_s=40)

        # Start geckodriver on a fixed port (localhost only).
        gecko_proc = subprocess.Popen(
            ["geckodriver", "--port", "4444", "--host", "127.0.0.1"],
            stdout=subprocess.DEVNULL,
            stderr=subprocess.DEVNULL,
        )
        try:
            time.sleep(1)
            capture_screenshot(
                app_url=app_url,
                out_png=args.out,
                geckodriver_url="http://127.0.0.1:4444",
                wait_ready_contains=str(args.wait_ready),
                wait_timeout_s=int(args.wait_timeout),
                width=int(args.width),
                height=int(args.height),
            )
        finally:
            gecko_proc.terminate()
            gecko_proc.wait(timeout=10)
    finally:
        proc.terminate()
        proc.wait(timeout=10)

    if not args.out.exists() or args.out.stat().st_size < 1024:
        raise RuntimeError(f"Screenshot seems invalid: {args.out}")
    print("Wrote:", args.out)
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
