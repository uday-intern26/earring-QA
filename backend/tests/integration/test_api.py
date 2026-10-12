import io

from fastapi.testclient import TestClient
from PIL import Image

from app.main import app


def test_health_and_openapi():
    with TestClient(app) as client:
        health = client.get("/api/v1/health")
        assert health.status_code == 200
        assert health.json()["database"] == "ok"
        docs = client.get("/openapi.json")
        assert docs.status_code == 200
        paths = docs.json()["paths"]
        assert "/api/v1/applications/validate" in paths
        assert "/api/v1/tests/{test_id}/run" in paths
        assert "/api/v1/tests/{test_id}/report" in paths


def test_reference_upload_and_test_create_do_not_echo_a_password():
    with TestClient(app) as client:
        created = client.post(
            "/api/v1/applications",
            json={"name": "Amplify", "type": "web", "url": "https://example.amplifyapp.com", "username": "tester"},
        )
        assert created.status_code == 201
        assert "password" not in created.json()
        image = Image.new("RGB", (64, 48), (20, 20, 20))
        buffer = io.BytesIO()
        image.save(buffer, format="PNG")
        uploaded = client.post(
            "/api/v1/references/upload",
            files={"file": ("reference-earring-correct.png", buffer.getvalue(), "image/png")},
            data={"side": "left"},
        )
        assert uploaded.status_code == 201
        body = uploaded.json()
        assert body["filename"] == "reference-earring-correct.png"
        assert body["width"] == 64
        assert body["height"] == 48
        listed = client.get("/api/v1/references")
        assert listed.status_code == 200
        assert listed.json()[0]["id"] == body["id"]
        test = client.post(
            "/api/v1/tests",
            json={
                "name": "Left Earring Placement Test",
                "application_id": created.json()["id"],
                "reference_id": body["id"],
                "jewelry_id": "E123",
                "jewelry_type": "earring",
                "ear_side": "left",
                "capture_fps": 5,
                "minimum_confidence": 0.8,
                "pass_threshold": 0.10,
                "fail_threshold": 0.15,
                "minimum_pass_rate": 0.95,
                "maximum_consecutive_failures": 2,
            },
        )
        assert test.status_code == 201
        assert "password" not in test.json()
        rejected = client.post(
            "/api/v1/references/upload",
            files={"file": ("notes.txt", b"hello", "text/plain")},
        )
        assert rejected.status_code == 422


def test_invalid_url_fails_without_opening_a_browser():
    with TestClient(app) as client:
        response = client.post(
            "/api/v1/applications/validate",
            json={"url": "not a url", "username": "tester", "password": "secret-value"},
        )
        assert response.status_code == 200
        payload = response.json()
        assert payload["status"] == "failed"
        assert payload["reachable"] is False
        assert "secret-value" not in response.text
