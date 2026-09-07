.PHONY: setup backend frontend

setup:
	pip install -r requirements.txt
	python3 -m src.combine_datasets
	python3 -m src.clean_amount
	python3 -m src.clean_dates
	python3 -m src.clean_categories
	python3 -m src.clean_payment_mode
	python3 -m src.dedupe
	python3 -m src.anomaly_detection
	python3 -m src.chunking
	python3 -m src.embed_and_store

backend:
	python3 -m uvicorn api.main:app --port 8000

frontend:
	cd frontend && [ -f .env.local ] || cp .env.local.example .env.local
	cd frontend && npm install && npm run dev
