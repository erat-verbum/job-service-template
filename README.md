# Job Service Template

Generic FastAPI service template for running a single job at a time. Copy and customize this template to create new services.

## Features

- FastAPI-based REST API
- Job management (start, status, cancel)
- Single job at a time (returns 409 Conflict if a job is already running)
- Progress tracking
- Health check endpoint
- Pydantic models for data validation
- Docker support
- Unit and integration tests

## Quick Start

```bash
make install  # Install dependencies
make run      # Start the service
```

## API Endpoints

- `GET /health` - Health check
- `POST /job` - Start a job (returns 409 if a job is already running)
- `GET /job` - Get job status
- `POST /job/cancel` - Cancel running job

## Commands

- `make install` - Install dependencies
- `make lint` - Run linters
- `make check` - Type checking
- `make test` - Run all tests
- `make run` - Start the service
