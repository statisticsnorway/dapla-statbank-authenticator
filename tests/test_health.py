import logging
from fastapi.testclient import TestClient
from app.main import app as api

client = TestClient(api)

logger = logging.getLogger()


def test_liveness():
    """Tests the liveness endpoint. Is always 200 for now"""
    response = client.get("/health/liveness")
    assert response.status_code == 200
    assert response.json() == {
        "name": "dapla-statbank-authenticator",
        "status": "UP"
    }


def test_readiness():
    """Tests the readiness endpoint. Is always 200 for now"""
    response = client.get("/health/readiness")

    assert response.status_code == 200
