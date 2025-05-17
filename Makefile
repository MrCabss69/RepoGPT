.PHONY: test lint type cov

lint:
	ruff check src tests --fix

type:
	mypy src tests

# cov:
# 	pytest --cov=src/repogpt --cov-report=html \
# 	       --cov-report=xml:coverage.xml
# 	@echo "Open htmlcov/index.html"


test:
	pytest tests/ -v

clean:
	find . -type d -name __pycache__ -exec rm -rf {} +
	find . -type d -name .pytest_cache -exec rm -rf {} +
	find . -type f -name "*.pyc" -delete

repogpt:
	python -m repogpt.app.cli:main