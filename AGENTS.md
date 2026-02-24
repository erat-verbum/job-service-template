# Service Template: Generic FastAPI Service

Purpose: Template for enhancia-3 services. FastAPI app with Pydantic models, tests, Makefile/Docker. Copy/customize for new services (e.g., video processing).

## File Tree

```
src/
├── main.py              # FastAPI entry point with HTTP endpoints
└── models.py            # Pydantic models for requests, responses, and data structures

test/
└── unit/                # Unit tests (test__main__health.py etc.)
```

## File Explanations

- **main.py**: FastAPI application with a simple health check endpoint (`GET /health`). Returns service status and basic information.

- **models.py**: Pydantic models defining response schemas for the health check endpoint, including status enums and response data structures.

## HTTP Interface

- `GET /health`
  - **Response**: Health status object with:
    ```json
    {
      "status": "healthy|unhealthy|degraded",
      "message": "string",
      "timestamp": "ISO timestamp",
      "service_name": "string"
    }
    ```

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