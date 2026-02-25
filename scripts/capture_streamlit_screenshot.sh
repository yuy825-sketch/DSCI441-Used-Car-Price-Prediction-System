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
  else
    if "$STREAMLIT_BIN" - <<'PY' >/dev/null 2>&1
import urllib.request
urllib.request.urlopen("http://127.0.0.1:8501", timeout=1).read(1)
PY
    then
      break
    fi
  fi
  sleep 1
done

sleep 2
mkdir -p "$(dirname "$OUT_PNG")"

# Snap Firefox can be restrictive; capture into $HOME (non-hidden) then copy.
TMP_PNG="$HOME/dsci441_streamlit_demo.png"
rm -f "$TMP_PNG"

echo "Capturing screenshot -> $TMP_PNG"
firefox --headless --window-size 1400,900 --screenshot "$TMP_PNG" "$URL" >/dev/null 2>&1 || true
cp -f "$TMP_PNG" "$OUT_PNG"

if [[ ! -s "$OUT_PNG" ]]; then
  echo "ERROR: screenshot failed. See /tmp/dsci441_streamlit.log" >&2
  exit 2
fi

echo "Wrote: $OUT_PNG"
