# Job Service Template: Generic FastAPI Service

Purpose: Generic FastAPI service template with job management. FastAPI app with Pydantic models, tests, Makefile/Docker. Copy/customize for new services.

## Development Workflow

1. **Clarify requirements**: Ask clarifying questions of the user to understand the task fully.
2. **Plan the approach**: Create/update a TODO list to outline the steps needed to complete the task.
3. **Research**: Use context7 to look up how libraries work when needed for the task.
4. **Implement**: Make targeted, small changes, one-by-one to ensure quality and avoid errors.
5. **Verify**: Read the modified files to ensure the changes are correct.
6. **Lint and Type Check**: Run linting (`make lint`), fix linting issues (`make lint-fix`), and type checking (`make check`) to ensure code quality.
7. **Test**: Run tests to verify functionality. Then run tests (`make test` for all, `make test-unit`/`make test-int` for specific types).
8. **Complete**: Do not stop until all tasks on the TODO list are completed and verified.

## Rules of Engagement

1. Think incredibly hard and long before getting to the Implement step, writing lots and lots, considering all possible options and then choosing the right one
2. Be concise specifically when responding to the user that a task has been completed

## Makefile Usage

Before running any command, read the relevant Makefile.

### Service-level commands

- `make install`: uv venv/sync
- `make lint lint-fix check`: ruff/pyright
- `make test test-unit test-int`: pytest
- `make run`: uvicorn

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

## Project Folder Structure

Each service follows this folder structure:

```
service-name/
├── Dockerfile      # Container configuration
├── .venv/          # Virtual environment (created by uv)
├── pyproject.toml  # Project configuration
├── Makefile        # Common commands
├── src/
│   ├── main.py     # FastAPI application
│   ├── models.py   # Pydantic models and data structures
│   └── job_runner.py  # Job execution logic
└── test/
    ├── unit/       # Unit tests
    │   └── test__<name_of_file_being_tested>__<name_of_feature_being_tested>.py
    └── integration/ # Integration tests
        └── test__<name_of_file_being_tested>__<name_of_feature_being_tested>.py
```

## Service Components

- **Dockerfile**: Container configuration for the service
- **uv**: Package manager (installed in local `.venv`)
- **ruff**: Linting and formatting
- **pyright**: Type checking
- **FastAPI**: Interface with other services
- **pyproject.toml**: Project configuration
- **Python `requests` library**: For making HTTP API calls to external services
- **Pydantic**: For data validation and serialization - Pydantic models should be defined for every non-simple object
- **Type annotations**: All method parameters and return types must be annotated for better code quality and IDE support
- **Docstrings**: Each method must include a docstring with: a description, Args section (parameter names, types, descriptions), Returns section (return type and description), and Raises section (exceptions and when they're raised). Format example:
  ```
  def method_name(self, param1: Type) -> ReturnType:
      """
      Brief description of the method.
      
      Args:
          param1 (Type): Description of parameter
      
      Returns:
          ReturnType: Description of return value
      
      Raises:
          ExceptionType: Description of when this exception is raised
      """
  ```
- **Class method organization**: Public methods in a class should always be written at the bottom of the class AFTER all of the private methods (those starting with underscore). This improves code readability by grouping implementation details together.
- **Test naming**: Test files should be named:
  - `test__<name_of_file_being_tested>.py` for simple cases where the file contains tests for a single feature
  - `test__<name_of_file_being_tested>__<name_of_feature_being_tested>.py` when the file would become too large or contain tests for multiple distinct features

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