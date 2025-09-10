# Running the Lead Assessment POC

This guide is a concise, copy/paste friendly version for new contributors. For deeper detail see `RUNTIME_GUIDE.md`.

## 1. Prerequisites
- Python 3.10+ (3.11+ recommended)
- Node.js 18+ (LTS)
- npm 9+
- Git
- (Optional) Docker + Docker Compose

## 2. Clone & Enter
```
git clone <repo-url>
cd Lead_Assessment_POC
```

## 3. Environment Variables
Copy the sample env file and edit as needed.
```
cp env.example .env
```
Set (optional) AI key to enable Gemini summaries & outreach:
```
GEMINI_API_KEY=<your_gemini_api_key>
```
Leaving it unset = fallback non-AI summaries.

Optional fast flags:
- `FAST_START=true`  (skip model load / training – mock predictions)
- `SKIP_TRAIN=true`  (generate data but skip training)

## 4. One‑Command Startup (recommended)
```
FAST_START=true ./start_app.sh
```
Then open:
- Frontend: http://localhost:3000
- API Docs: http://localhost:8000/docs
- Health:   http://localhost:8000/health

## 5. Manual Startup (if you prefer separate terminals)
Terminal 1 (backend):
```
python -m venv venv
source venv/bin/activate
pip install -r requirements.txt
python data_generator.py
python ml_models.py   # optional (skip if FAST_START behaviour desired)
uvicorn backend.main:app --host 0.0.0.0 --port 8000 --reload
```
Terminal 2 (frontend):
```
cd frontend
npm install
npm start
```

## 6. Basic Smoke Test
```
curl -s http://localhost:8000/health
curl -s 'http://localhost:8000/api/leads?limit=2' | head
```

## 7. Docker (production-style bundle)
Build and run (serves frontend via nginx + backend):
```
docker build -t lead-assessment .
# Optionally pass GEMINI key at runtime
docker run -p 80:80 -p 8000:8000 --env GEMINI_API_KEY=<your_gemini_api_key> lead-assessment
```
Then:
- Frontend: http://localhost/
- API:      http://localhost:8000/

(If you add a docker-compose.yml service for frontend/backend separately, adjust host ports accordingly.)

## 8. Regenerating Data / Retraining
```
source venv/bin/activate
rm -rf data models
python data_generator.py
python ml_models.py
```
Restart backend afterwards.

## 9. Common Env Vars
| Variable | Purpose | Default |
|----------|---------|---------|
| GEMINI_API_KEY | Enables AI summaries/outreach | (unset) |
| API_PORT | Backend port (start_app.sh) | 8000 |
| FAST_START | Skip model load (mock predictions) | false |
| SKIP_TRAIN | Skip model training | false |

## 10. Logs (start_app.sh)
- backend.log
- frontend.log

## 11. Stopping (Now Easier)
Preferred:
```
./stop_all.sh
```
Supports `FORCE=1` to escalate if a process refuses to die.

Legacy/manual (not needed usually):
```
kill $(cat .app_backend.pid 2>/dev/null) $(cat .app_frontend.pid 2>/dev/null)
# or patterns
pkill -f uvicorn
pkill -f react-scripts
```

PID files: `.app_backend.pid`, `.app_frontend.pid` are created automatically.

## 12. Restart Convenience
```
./restart.sh                 # normal restart
FAST_START=1 ./restart.sh    # quick restart (mock predictions)
API_PORT=8001 ./restart.sh   # change backend port
```

Under the hood it runs `stop_all.sh` then `start_app.sh`.

## 13. Troubleshooting Quick List
| Issue | Check |
|-------|-------|
| 8000 in use | `lsof -i :8000` then kill process |
| Frontend blank | Open DevTools Console; verify API 200s |
| AI summary says unavailable | Ensure `GEMINI_API_KEY` exported before start |
| Models not loading | Delete `models/` and rerun training | 

## 14. Security Notes
- Never commit real API keys. `.env` is git-ignored (verify in `.gitignore`).
- Use placeholders (`<your_gemini_api_key>`) in docs and examples.

---
Happy building! Let me know if you want a Makefile or compose profile next.
