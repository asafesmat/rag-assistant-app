from fastapi.testclient import TestClient
from app.main import app

with TestClient(app) as client:

    def test_health():
        r = client.get("/health")
        assert r.status_code == 200
        assert r.json() == {"status": "ok"}

    def test_query_happy_path():
        r = client.post("/query", json={"question": "هل أقدر أرجّع سلعة واسترد فلوسي؟"})
        assert r.status_code == 200
        body = r.json()
        assert "answer" in body and "sources" in body
        assert len(body["sources"]) > 0

    def test_query_invalid_input():
        r = client.post("/query", json={"wrong_field": "test"})
        assert r.status_code == 422