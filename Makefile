.PHONY: help install dev test lint format clean run docker-up docker-down build-package check-package publish-test publish-pypi publish-js publish-js-dry

help:
	@echo "Available commands:"
	@echo "  make install         - Install dependencies"
	@echo "  make dev            - Install development dependencies"
	@echo "  make test           - Run all tests"
	@echo "  make test-no-llm    - Run basic non-LLM integration tests (25 tests)"
	@echo "  make test-comprehensive - Run comprehensive tests (70+ tests)"
	@echo "  make test-all-integration - Run all integration tests (125+ tests)"
	@echo "  make test-performance - Run performance/load tests"
	@echo "  make test-api       - Run Python feature tests"
	@echo "  make test-all-features - Run shell-based feature tests"
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

test-no-llm:
	pytest tests/integration/test_api_no_llm.py -v

test-comprehensive:
	pytest tests/integration/test_api_comprehensive.py -v

test-all-integration:
	pytest tests/integration/ -v

test-performance:
	pytest tests/integration/test_performance.py -v -s

test-api:
	python3 test_features_python.py --skip-llm

test-all-features:
	./test_all_features.sh

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
	@python3 -c "from config.settings import get_settings; s = get_settings(); print(f'Starting server on {s.server_host}:{s.server_port}')" || echo "Starting server..."
	uvicorn src.api.main:app --reload --host $$(python3 -c "from config.settings import get_settings; print(get_settings().server_host)") --port $$(python3 -c "from config.settings import get_settings; print(get_settings().server_port)")

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

