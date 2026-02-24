# Service Template: Generic FastAPI Service

Purpose: Template for enhancia-3 services. FastAPI app with Pydantic models, tests, Makefile/Docker. Copy/customize for new services (e.g., video processing).

## File Tree

```
src/
├── main.py              # FastAPI entry point with HTTP endpoints
├── models.py            # Pydantic models for requests, responses, and data structures
└── job_runner.py       # Job execution logic with progress and cancellation support

test/
└── unit/                # Unit tests (test__main__health.py etc.)
```

## File Explanations

- **main.py**: FastAPI application with endpoints:
  - `GET /health` - Health check
  - `POST /job` - Start a job
  - `GET /job` - Get current job status
  - `POST /job/cancel` - Cancel running job

- **models.py**: Pydantic models including `Job`, `JobStatus`, `StartJobRequest`, and health check responses.

- **job_runner.py**: Placeholder job implementation. Modify `run_job()` to implement actual job logic.

## HTTP Interface

### Health Check

- `GET /health`
  - **Response**:
    ```json
    {
      "status": "healthy|unhealthy|degraded",
      "message": "string",
      "timestamp": "ISO timestamp",
      "service_name": "string"
    }
    ```

### Job Management

- `POST /job`
  - **Request Body**:
    ```json
    {
      "job_id": "string",
      "input_params": { "key": "value" }
    }
    ```
  - **Response**: Job object with status, progress, timestamps
  - **Errors**: 409 if job already running

- `GET /job`
  - **Response**: Job object or `null` if no job exists
    ```json
    {
      "id": "string",
      "status": "running|completed|failed|cancelled",
      "progress": 0-100,
      "result": { ... },
      "error": "string",
      "created_at": "ISO timestamp",
      "started_at": "ISO timestamp",
      "finished_at": "ISO timestamp"
    }
    ```

- `POST /job/cancel`
  - **Request Body**: `{}` (empty)
  - **Response**: `{"message": "Job cancelled"}`
  - **Errors**: 404 if no job, 400 if job not running

## Dockerfile Requirements

The Dockerfile must include:
```dockerfile
RUN make install && \
    make lint && \
    make check
```

## Makefile (service-level)

- `make install`: uv venv/sync
- `make lint lint-fix check`: ruff/pyright
- `make test test-unit test-int`: pytest
- `make run`: uvicorn
- Root: `make up-{service} test-{service}`