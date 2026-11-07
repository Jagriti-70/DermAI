import sys
from pathlib import Path

PROJECT_ROOT = Path(__file__).resolve().parents[1]
APP_ROOT = PROJECT_ROOT / "prototypes" / "flask-tensorflow-demo"
sys.path.insert(0, str(APP_ROOT))

from backend.app import app  # noqa: E402


def test_health_endpoint_reports_backend():
    client = app.test_client()
    response = client.get("/api/health")
    assert response.status_code == 200
    payload = response.get_json()
    assert payload["status"] == "ok"
    assert payload["backend"] in {"heuristic", "tensorflow"}
    assert payload["classes"] == 10


def test_classes_endpoint_returns_configured_classes():
    client = app.test_client()
    response = client.get("/api/classes")
    assert response.status_code == 200
    payload = response.get_json()
    assert len(payload["classes"]) == 10
    assert all("name" in item for item in payload["classes"])


def test_predict_requires_image():
    client = app.test_client()
    response = client.post("/api/predict", data={})
    assert response.status_code == 400
    assert "error" in response.get_json()
