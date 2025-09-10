PYTHON=python3
VENV=venv
ACTIVATE=. $(VENV)/bin/activate;

.PHONY: help install backend frontend start stop restart test lint build-frontend docker-build docker-up docker-down clean

help:
	@echo "Common targets:"
	@echo "  make install        - Install backend + frontend deps (venv + npm)"
	@echo "  make backend        - Backend deps only"
	@echo "  make frontend       - Frontend deps only"
	@echo "  make start          - FAST_START run via script"
	@echo "  make start-full     - Full run (training)"
	@echo "  make stop           - Stop processes"
	@echo "  make restart        - Restart (FAST_START)"
	@echo "  make test           - Run backend tests (pytest)"
	@echo "  make build-frontend - Production frontend build"
	@echo "  make docker-build   - Build container image"
	@echo "  make docker-up      - Run docker-compose"
	@echo "  make docker-down    - Stop docker-compose"
	@echo "  make clean          - Remove venv, node_modules, build artifacts"

install: backend frontend

backend:
	@if [ ! -d $(VENV) ]; then $(PYTHON) -m venv $(VENV); fi
	$(ACTIVATE) pip install -r requirements.txt

frontend:
	cd frontend && npm install

start:
	FAST_START=true ./start_app.sh

start-full:
	./start_app.sh

stop:
	./stop_all.sh || true

restart:
	FAST_START=true ./restart.sh

test:
	@if [ ! -d $(VENV) ]; then $(PYTHON) -m venv $(VENV); fi
	$(ACTIVATE) pip install -r requirements.txt >/dev/null
	$(ACTIVATE) pytest -q

build-frontend:
	cd frontend && npm run build

docker-build:
	docker build -t lead-assessment .

docker-up:
	docker compose up -d --build

docker-down:
	docker compose down

clean:
	rm -rf $(VENV) frontend/node_modules frontend/build .pytest_cache
	rm -f .app_backend.pid .app_frontend.pid
