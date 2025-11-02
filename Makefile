
.PHONY: init run dry docker-build docker-run format

init:
	python -m venv .venv
	. .venv/bin/activate && pip install -r requirements.txt

run:
	. .venv/bin/activate && python main.py

dry:
	. .venv/bin/activate && python main.py --dry-run

docker-build:
	docker build -t litfeed-bot:latest .

docker-run:
	docker run --rm -e GOOGLE_API_KEY -e MM_WEBHOOK_URL litfeed-bot:latest
