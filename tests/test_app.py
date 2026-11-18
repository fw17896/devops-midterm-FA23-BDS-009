from fastapi.testclient import TestClient
from app import app

client = TestClient(app)


def test_health():
    response = client.get("/health")
    assert response.status_code == 200
    assert response.json()["status"] == "ok"


def test_metrics():
    response = client.get("/metrics")
    assert response.status_code == 200

    data = response.json()

    assert data["student_id"] == "FA23-BDS-009"
    assert data["accuracy"] >= 0
    assert data["training_rows"] >= 100
    assert data["model_version"]
    assert data["git_sha"]


def test_prediction():
    response = client.post(
        "/predict",
        json={
            "records": [
                {
                    "engine_load": 75,
                    "road_delay": 20,
                    "fuel_variance": 5,
                    "driver_hours": 8
                }
            ]
        }
    )

    assert response.status_code == 200
