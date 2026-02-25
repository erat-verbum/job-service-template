import os
import time
from typing import Any, Optional

import httpx
import pytest


BASE_URL = os.environ.get("INTEGRATION_TEST_URL", "http://localhost:8001")
POLL_INTERVAL = 0.5
POLL_TIMEOUT = 5


@pytest.fixture
def client():
    return httpx.Client(base_url=BASE_URL, timeout=30.0)


@pytest.fixture(autouse=True)
def reset_job_state(client):
    """Ensure no job is running before each test, wait for any existing job to complete."""
    response = client.get("/job")
    if response.status_code == 200 and response.json() is not None:
        job = response.json()
        if job["status"] == "running":
            client.post("/job/cancel")
    yield
    response = client.get("/job")
    if response.status_code == 200 and response.json() is not None:
        job = response.json()
        if job["status"] == "running":
            client.post("/job/cancel")


def wait_for_job_completion(
    client: httpx.Client, job_id: str
) -> Optional[dict[str, Any]]:
    """Poll GET /job until status is not 'running' or timeout."""
    start_time = time.time()
    job: Optional[dict[str, Any]] = None
    while time.time() - start_time < POLL_TIMEOUT:
        response = client.get("/job")
        assert response.status_code == 200
        job = response.json()
        if job is None:
            return None
        if job["status"] != "running":
            return job
        time.sleep(POLL_INTERVAL)
    return job


def test_health_check_in_container(client):
    """Test GET /health returns healthy status."""
    response = client.get("/health")
    assert response.status_code == 200
    data = response.json()
    assert data["status"] == "healthy"
    assert "timestamp" in data
    assert data["service_name"] == "template-service"


def test_get_job_empty_in_container(client):
    """Test GET /job returns null when no job exists."""
    response = client.get("/job")
    assert response.status_code == 200
    assert response.json() is None


def test_start_job_in_container(client):
    """Test POST /job starts a new job."""
    response = client.post("/job", json={"job_id": "test-job-1"})
    assert response.status_code == 200
    data = response.json()
    assert data["id"] == "test-job-1"
    assert data["status"] == "running"
    assert data["progress"] == 0


def test_get_job_returns_running(client):
    """Test GET /job returns current running job with progress."""
    client.post("/job", json={"job_id": "running-job"})

    response = client.get("/job")
    assert response.status_code == 200
    data = response.json()
    assert data["id"] == "running-job"
    assert data["status"] == "running"
    assert "progress" in data
    assert data["progress"] >= 0


def test_job_completes_in_container(client):
    """Test POST /job, wait for completion, verify result."""
    response = client.post("/job", json={"job_id": "completed-job"})
    assert response.status_code == 200

    job = wait_for_job_completion(client, "completed-job")

    assert job is not None
    assert job["status"] == "completed"
    assert job["result"] is not None
    assert job["finished_at"] is not None
    assert job["result"].get("completed") is True
    assert job["result"].get("total_steps") == 10


def test_cannot_start_job_while_running(client):
    """Test POST /job while job is running returns 409."""
    client.post("/job", json={"job_id": "first-job"})

    response = client.post("/job", json={"job_id": "second-job"})
    assert response.status_code == 409
    assert "already running" in response.json()["detail"]


def test_cancel_running_job(client):
    """Test POST /job/cancel cancels running job."""
    client.post("/job", json={"job_id": "cancel-job"})

    response = client.post("/job/cancel")
    assert response.status_code == 200

    response = client.get("/job")
    assert response.status_code == 200
    job = response.json()
    assert job["status"] == "cancelled"
    assert job["finished_at"] is not None


def test_cancel_no_job(client):
    """Test POST /job/cancel when no running job returns 400."""
    response = client.post("/job/cancel")
    assert response.status_code == 400


def test_cancel_completed_job(client):
    """Test POST /job/cancel on completed job returns 400."""
    client.post("/job", json={"job_id": "already-done"})

    wait_for_job_completion(client, "already-done")

    response = client.post("/job/cancel")
    assert response.status_code == 400


def test_job_with_input_params(client):
    """Test POST /job with input_params stores and returns them."""
    input_params = {"video_url": "s3://bucket/video.mp4", "quality": "1080p"}
    response = client.post(
        "/job", json={"job_id": "params-job", "input_params": input_params}
    )
    assert response.status_code == 200
    data = response.json()
    assert data["input_params"] == input_params

    response = client.get("/job")
    assert response.status_code == 200
    assert response.json()["input_params"] == input_params
