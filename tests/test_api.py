import os, sys
from fastapi.testclient import TestClient

# Ensure root directory is on path when running tests from repo root
ROOT = os.path.abspath(os.path.join(os.path.dirname(__file__), '..'))
if ROOT not in sys.path:
    sys.path.insert(0, ROOT)

from backend.main import app

client = TestClient(app)

def test_health():
    r = client.get('/health')
    assert r.status_code == 200
    body = r.json()
    assert body.get('status') == 'healthy'

def test_root():
    r = client.get('/')
    assert r.status_code == 200
    body = r.json()
    assert body.get('message') == 'Lead Assessment POC API'

def test_leads_404_without_data():
    # CSVs are git-ignored, so in CI the data file is absent -> 404 expected
    r = client.get('/api/leads?limit=5')
    assert r.status_code in (200, 404)
    # If data exists locally developer still passes
