.PHONY: install format lint test run-api run-dashboard clean

PYTHON = python
PIP = pip
UVICORN = uvicorn
STREAMLIT = streamlit

install:
	$(PIP) install -r requirements.txt
	$(PIP) install -e .[dev]

format:
	black app tests dashboard app_hf.py

lint:
	ruff check app tests dashboard app_hf.py
	black --check app tests dashboard app_hf.py

test:
	pytest tests/ -v

run-api:
	$(UVICORN) app.main:app --reload --port 8000

run-dashboard:
	$(STREAMLIT) run dashboard/app.py --server.port 8501

clean:
	rm -rf __pycache__ .pytest_cache .ruff_cache app/__pycache__ app/db/__pycache__ app/services/__pycache__ app/schemas/__pycache__ app/core/__pycache__ dashboard/__pycache__
	rm -f app/db/autopilot.db
