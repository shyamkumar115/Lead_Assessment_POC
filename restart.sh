#!/bin/bash

###############################################
# restart.sh
# Stops running backend/frontend then starts fresh
# passing any env flags to start_app.sh.
#
# Examples:
#   ./restart.sh
#   FAST_START=1 ./restart.sh
#   FAST_START=1 SKIP_TRAIN=1 API_PORT=8001 ./restart.sh
###############################################

set -euo pipefail
ROOT_DIR="$(cd "$(dirname "$0")" && pwd)"
cd "$ROOT_DIR"

echo "== Stopping existing processes =="
./stop_all.sh || true

echo "== Starting application =="
./start_app.sh

echo "Restart complete." 
