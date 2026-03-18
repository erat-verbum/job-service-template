.PHONY: install lint check quality test test-unit test-int run run-cli

install:
	uv venv --clear
	uv sync
	uv run pre-commit install

lint:
	uv run ruff check src test --fix

check:
	PYTHONPATH=. uv run ty check src test

quality:
	uv run bandit -c pyproject.toml -r src test
	uv run xenon --max-average=B --max-modules=C --max-absolute=C src
	uv run vulture --min-confidence=80 src test

test:
	PYTHONPATH=. uv run pytest --cov=src --cov-report=term-missing --tb=short

test-unit:
	PYTHONPATH=. uv run pytest test/unit/ -v --tb=short

test-int:
	PYTHONPATH=. uv run pytest test/integration/ -v --tb=short

run:
	uv run uvicorn src.main:app --host 0.0.0.0 --port 8001

run-cli:
	PYTHONPATH=. uv run python -m src.cli

docker-build:
	docker build -t job-service-template .

docker-run:
	docker run -p 8001:8001 job-service-template

up:
	docker-compose up -d

up-build:
	docker-compose up -d --build

down:
	docker-compose down