.PHONY: help install dev test lint format clean run docker-up docker-down build-package check-package publish-test publish-pypi publish-js publish-js-dry

help:
	@echo "Available commands:"
	@echo "  make install         - Install dependencies"
	@echo "  make dev            - Install development dependencies"
	@echo "  make test           - Run tests"
	@echo "  make lint           - Run linters"
	@echo "  make format         - Format code"
	@echo "  make clean          - Clean build artifacts"
	@echo "  make run            - Run application"
	@echo "  make docker-up      - Start Docker services"
	@echo "  make docker-down    - Stop Docker services"
	@echo ""
	@echo "Publishing commands:"
	@echo "  make build-package  - Build Python package"
	@echo "  make check-package  - Check package before publishing"
	@echo "  make publish-test   - Publish to TestPyPI"
	@echo "  make publish-pypi   - Publish to PyPI"
	@echo "  make publish-js     - Publish JavaScript SDK to npm"
	@echo "  make publish-js-dry  - Dry run for JavaScript SDK"

install:
	pip install -r requirements.txt

dev:
	pip install -r requirements.txt
	pip install -e .

test:
	pytest tests/ -v

lint:
	flake8 src/ tests/
	mypy src/

format:
	black src/ tests/
	isort src/ tests/

clean:
	find . -type d -name __pycache__ -exec rm -r {} +
	find . -type f -name "*.pyc" -delete
	find . -type f -name "*.pyo" -delete
	find . -type d -name "*.egg-info" -exec rm -r {} +
	rm -rf .pytest_cache
	rm -rf .mypy_cache
	rm -rf build dist

run:
	uvicorn src.api.main:app --reload --host 0.0.0.0 --port 8000

docker-up:
	docker-compose up -d

docker-down:
	docker-compose down

docker-logs:
	docker-compose logs -f

setup-vector-db:
	python scripts/setup_vector_db.py

load-databases:
	python scripts/load_databases.py

index-db:
	@echo "Usage: make index-db DB_ID=<database_id>"
	python scripts/index_database.py $(DB_ID)

# Publishing commands
build-package:
	python -m build

check-package:
	twine check dist/*

publish-test:
	twine upload --repository testpypi dist/*

publish-pypi:
	twine upload dist/*

publish-js:
	cd src/sdk/javascript && npm run build && npm publish

publish-js-dry:
	cd src/sdk/javascript && npm run build && npm publish --dry-run

