UV ?= $(shell which uv 2>/dev/null || echo $(HOME)/.local/bin/uv)

.PHONY: lint format typecheck test test-cov clean

lint:
	$(UV) run ruff check src tests

format:
	$(UV) run ruff format src tests

typecheck:
	$(UV) run mypy src tests

test:
	$(UV) run pytest tests/ -q

test-cov:
	$(UV) run pytest tests/ --cov=design_patterns --cov-report=term-missing --cov-fail-under=95


clean:
	find . -type d -name __pycache__ -exec rm -rf {} +
	find . -type d -name .mypy_cache -exec rm -rf {} +
	find . -type d -name .pytest_cache -exec rm -rf {} +
	find . -type d -name .ruff_cache -exec rm -rf {} +
