import pytest
from fastapi.testclient import TestClient

from src.main import app, reset_job


@pytest.fixture(autouse=True)
def reset_state():
    """Reset job state before each test."""
    reset_job()
    yield
    reset_job()


@pytest.fixture
def client():
    return TestClient(app)


def test_health_check(client):
    """Test health check endpoint."""
    response = client.get("/health")
    assert response.status_code == 200
    data = response.json()
    assert data["status"] == "healthy"
    assert "timestamp" in data


def test_get_job_empty(client):
    """Test GET /job returns empty when no job exists."""
    response = client.get("/job")
    assert response.status_code == 200
    assert response.json() is None


def test_start_job(client):
    """Test POST /job starts a new job."""
    response = client.post("/job", json={"job_id": "test-job-1"})
    assert response.status_code == 200
    data = response.json()
    assert data["id"] == "test-job-1"
    assert data["status"] == "running"
    assert data["progress"] == 0


def test_start_job_rejects_when_running(client):
    """Test POST /job returns 409 when job already running."""
    client.post("/job", json={"job_id": "job-1"})

    response = client.post("/job", json={"job_id": "job-2"})
    assert response.status_code == 409
    assert "already running" in response.json()["detail"]


def test_get_job_returns_current(client):
    """Test GET /job returns current job."""
    client.post("/job", json={"job_id": "my-job"})

    response = client.get("/job")
    assert response.status_code == 200
    data = response.json()
    assert data["id"] == "my-job"
    assert data["status"] == "running"


def test_cancel_job(client):
    """Test POST /job/cancel cancels running job."""
    client.post("/job", json={"job_id": "cancel-me"})

    response = client.post("/job/cancel")
    assert response.status_code == 200

    response = client.get("/job")
    assert response.json()["status"] == "cancelled"


def test_cancel_job_no_job(client):
    """Test POST /job/cancel returns 404 when no job."""
    response = client.post("/job/cancel")
    assert response.status_code == 404


def test_cancel_job_completed(client):
    """Test POST /job/cancel returns 400 when job completed."""
    from unittest.mock import patch

    async def quick_job(job_ref, get_status):
        job_ref["progress"] = 100
        job_ref["status"] = "completed"
        return {"done": True}

    with patch("src.main.run_job", quick_job):
        response = client.post("/job", json={"job_id": "done-job"})
        assert response.status_code == 200

    response = client.post("/job/cancel")
    assert response.status_code == 400
