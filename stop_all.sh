#!/bin/bash

###############################################
# stop_all.sh
# Gracefully stop backend (uvicorn) and frontend (React dev server)
# Started via start_app.sh or manual runs.
#
# Order of preference for PID discovery:
# 1. PID files (.app_backend.pid / .app_frontend.pid)
# 2. Pattern match (uvicorn backend.main / react-scripts / npm start)
#
# Usage:
#   ./stop_all.sh            # normal stop
#   FORCE=1 ./stop_all.sh    # escalate to SIGKILL if graceful fails
###############################################

set -euo pipefail

ROOT_DIR="$(cd "$(dirname "$0")" && pwd)"
cd "$ROOT_DIR"

FORCE=${FORCE:-0}

grace_kill() {
  local pid=$1
  local name=$2
  if [ -z "$pid" ]; then
    return 0
  fi
  if ! kill -0 "$pid" 2>/dev/null; then
    return 0
  fi
  echo "Stopping $name (PID $pid) ..."
  kill "$pid" 2>/dev/null || true
  # wait up to 5s
  for i in {1..10}; do
    if kill -0 "$pid" 2>/dev/null; then
      sleep 0.5
    else
      echo "$name stopped"
      return 0
    fi
  done
  if kill -0 "$pid" 2>/dev/null; then
    if [ "$FORCE" = "1" ]; then
      echo "Force killing $name (PID $pid)"
      kill -9 "$pid" 2>/dev/null || true
    else
      echo "WARNING: $name still running (PID $pid). Re-run with FORCE=1 to force kill." >&2
    fi
  fi
}

backend_pid=""
frontend_pid=""

# Use PID files first
if [ -f .app_backend.pid ]; then
  backend_pid=$(cat .app_backend.pid || true)
fi
if [ -f .app_frontend.pid ]; then
  frontend_pid=$(cat .app_frontend.pid || true)
fi

# Fallback discovery if empty
if [ -z "$backend_pid" ]; then
  backend_pid=$(pgrep -f 'uvicorn[[:space:]].*backend.main' | head -n1 || true)
fi
if [ -z "$frontend_pid" ]; then
  # react-scripts or vite or npm start (react-scripts) patterns
  frontend_pid=$(pgrep -f 'react-scripts start' | head -n1 || pgrep -f 'node .*react-scripts' | head -n1 || true)
fi

if [ -z "$backend_pid" ] && [ -z "$frontend_pid" ]; then
  echo "No backend or frontend processes found."
else
  grace_kill "$backend_pid" "backend" || true
  grace_kill "$frontend_pid" "frontend" || true
fi

# Clean residual PID files if processes gone
for f in .app_backend.pid .app_frontend.pid; do
  if [ -f "$f" ]; then
    pid=$(cat "$f" || true)
    if [ -n "$pid" ] && kill -0 "$pid" 2>/dev/null; then
      # still alive: keep file
      :
    else
      rm -f "$f"
    fi
  fi
done

echo "Done." 
