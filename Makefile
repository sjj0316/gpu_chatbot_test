COMPOSE=docker compose --env-file .env.prod -f docker-compose.prod.yml

.PHONY: preflight build up down logs ps health smoke deploy-local rollback

preflight:
	@echo "[preflight] env keys..."
	bash scripts/preflight_env.sh
	@echo "[preflight] compose config..."
	bash scripts/preflight_compose.sh
	@echo "[preflight] OK"

build:
	$(COMPOSE) build

up:
	$(COMPOSE) up -d

down:
	$(COMPOSE) down

logs:
	$(COMPOSE) logs --tail=200

ps:
	$(COMPOSE) ps

health:
	@echo "[health] check for unhealthy containers in compose ps output"
	$(COMPOSE) ps

smoke:
	curl -fsS http://localhost/ >/dev/null
	curl -fsS http://localhost/api/openapi.json >/dev/null

deploy-local: preflight build up ps smoke
	@echo "[deploy-local] done"

rollback:
	@echo "[rollback] TODO: set TAG to <TAG_PREV> and run 'make up'"
