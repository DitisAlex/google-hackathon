install:
	python3 -m venv .venv && . .venv/bin/activate && pip install -r requirements-dev.txt

run:
	uvicorn src.main:app --host 0.0.0.0 --port 8000 --reload

test:
	pytest -v

lint:
	ruff check src tests

format:
	ruff format src tests

docker-build:
	docker build -t repo-doc-generator:latest .
