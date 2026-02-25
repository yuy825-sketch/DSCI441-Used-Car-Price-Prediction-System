#!/usr/bin/env bash
set -euo pipefail

REPO_ROOT="$(cd "$(dirname "${BASH_SOURCE[0]}")/.." && pwd)"

OUT_PNG="${1:-$REPO_ROOT/results/streamlit_demo.png}"
PORT="${PORT:-8501}"
ADDR="127.0.0.1"

# Use an existing trained run (not committed). Override by exporting DSCI441_DEMO_RUN_DIR.
DEFAULT_RUN_DIR="$REPO_ROOT/runs/20260225_155344__hgb-ordinal"
export DSCI441_DEMO_RUN_DIR="${DSCI441_DEMO_RUN_DIR:-$DEFAULT_RUN_DIR}"

STREAMLIT_BIN="$REPO_ROOT/.venv/bin/python"
if [[ ! -x "$STREAMLIT_BIN" ]]; then
  echo "ERROR: Missing venv python: $STREAMLIT_BIN" >&2
  exit 1
fi

if ! command -v firefox >/dev/null 2>&1; then
  echo "ERROR: firefox is required for screenshots (headless)." >&2
  exit 1
fi

cleanup() {
  if [[ -n "${STREAMLIT_PID:-}" ]] && kill -0 "$STREAMLIT_PID" >/dev/null 2>&1; then
    kill "$STREAMLIT_PID" >/dev/null 2>&1 || true
    wait "$STREAMLIT_PID" >/dev/null 2>&1 || true
  fi
}
trap cleanup EXIT

mkdir -p "$(dirname "$OUT_PNG")"

# Prefer the WebDriver path (waits for Streamlit to render; avoids blank screenshots).
if command -v geckodriver >/dev/null 2>&1; then
  echo "Capturing screenshot via geckodriver -> $OUT_PNG"
  "$STREAMLIT_BIN" "$REPO_ROOT/scripts/capture_streamlit_screenshot_webdriver.py" \
    --out "$OUT_PNG" \
    --addr "$ADDR" \
    --port "$PORT" \
    --wait-ready "Enter vehicle details" \
    --wait-timeout 120 \
    --width 1400 \
    --height 900
else
  echo "WARN: geckodriver not found; falling back to firefox --screenshot (may be blank)." >&2
  echo "Starting Streamlit on http://$ADDR:$PORT ..."
  "$STREAMLIT_BIN" -m streamlit run "$REPO_ROOT/app/app.py" \
    --server.headless true \
    --server.address "$ADDR" \
    --server.port "$PORT" >/tmp/dsci441_streamlit.log 2>&1 &
  STREAMLIT_PID="$!"

  URL="http://$ADDR:$PORT"
  echo "Waiting for server..."
  for _i in $(seq 1 40); do
    if command -v curl >/dev/null 2>&1; then
      if curl -fsS "$URL" >/dev/null 2>&1; then
        break
      fi
    fi
    sleep 1
  done

  sleep 2

  # Snap Firefox can be restrictive; capture into $HOME (non-hidden) then copy.
  TMP_PNG="$HOME/dsci441_streamlit_demo.png"
  rm -f "$TMP_PNG"

  echo "Capturing screenshot -> $TMP_PNG"
  firefox --headless --window-size 1400,900 --screenshot "$TMP_PNG" "$URL" >/dev/null 2>&1 || true
  cp -f "$TMP_PNG" "$OUT_PNG"
fi

if [[ ! -s "$OUT_PNG" ]]; then
  echo "ERROR: screenshot failed. See /tmp/dsci441_streamlit.log" >&2
  exit 2
fi

echo "Wrote: $OUT_PNG"
