# tests/test_main.py
from starlette.testclient import TestClient
from app.main import app

client = TestClient(app)

def test_health_check():
    response = client.get("/seedor/1.0/health")
    assert response.status_code == 200
    assert response.json() == {"status": "ok"}


def test_health_check():
    response = client.get("/seedor/1.0/health")
    assert response.status_code == 200
    assert response.json() == {"status": "ok"}
