.PHONY: dev prod down clean restart

ENV_FILE := .env
COMPOSE_BASE := infra/compose.yml
COMPOSE_DEV := infra/compose-dev.yml

dev:
	docker compose --env-file $(ENV_FILE) -f $(COMPOSE_BASE) -f $(COMPOSE_DEV) up -d

prod:
	docker compose --env-file $(ENV_FILE) -f $(COMPOSE_BASE) up -d

down:
	docker compose -f $(COMPOSE_BASE) down -v

clean: down

restart: down dev
