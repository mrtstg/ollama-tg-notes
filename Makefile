COMPOSE_COMMAND=docker compose --project-name ollama-notes --env-file docker.env -f deployment/docker-compose.yml

all: run

run: src/main.py
	poetry run python -m src.main

deploy-prod: deployment/docker-compose.yml
	$(COMPOSE_COMMAND) --profile prod up -d

destroy-prod: deployment/docker-compose.yml
	$(COMPOSE_COMMAND) --profile prod down

deploy-dev: deployment/docker-compose.yml
	$(COMPOSE_COMMAND) --profile dev up -d

destroy-dev: deployment/docker-compose.yml
	$(COMPOSE_COMMAND) --profile dev down
