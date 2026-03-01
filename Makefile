.PHONY: install dev test lint format run clean

install:
	pip install -e .

dev:
	pip install -e ".[dev]"

test:
	pytest tests/ -v

lint:
	ruff check src/ tests/
	mypy src/aain/

format:
	ruff format src/ tests/

run:
	uvicorn aain.app:create_app --factory --reload --port 8000

clean:
	find . -type d -name __pycache__ -exec rm -rf {} +
	find . -type d -name "*.egg-info" -exec rm -rf {} +
	rm -rf dist build .mypy_cache .pytest_cache htmlcov
