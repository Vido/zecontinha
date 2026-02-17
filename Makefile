# ============================
#        PROJECT COMMANDS
# ============================

.DEFAULT_GOAL := up
DOCKER_COMPOSE := $(shell docker compose version >/dev/null 2>&1 && echo "docker compose" || echo "docker-compose")

# ----------------------------
#        DOCKER BUILD
# ----------------------------

build:
	$(DOCKER_COMPOSE) build

build-no-cache:
	$(DOCKER_COMPOSE) build --no-cache

# ----------------------------
#        START SERVICES
# ----------------------------

up:
	$(DOCKER_COMPOSE) up --build -d --remove-orphans

up-dev:
	$(DOCKER_COMPOSE) -f docker-compose.yml -f docker-compose.dev.yml up --build --remove-orphans

up-db:
	$(DOCKER_COMPOSE) --profile db up -d --remove-orphans

up-cron:
	$(DOCKER_COMPOSE) --profile cron up -d --remove-orphans

# ----------------------------
#        STOP SERVICES
# ----------------------------

down:
	$(DOCKER_COMPOSE) down --remove-orphans

stop:
	$(DOCKER_COMPOSE) stop

restart:
	$(DOCKER_COMPOSE) down --remove-orphans
	$(DOCKER_COMPOSE) up -d --remove-orphans

# ----------------------------
#        LOGS
# ----------------------------

logs:
	$(DOCKER_COMPOSE) logs -f

logs-app:
	$(DOCKER_COMPOSE) logs -f app

logs-dev:
	$(DOCKER_COMPOSE) --profile dev logs -f

logs-db:
	$(DOCKER_COMPOSE) logs -f postgres

logs-cron:
	$(DOCKER_COMPOSE) logs -f cron

# ----------------------------
#        EXEC INTO CONTAINERS
# ----------------------------

bash:
	docker exec -it web-zecontinha bash && docker exec -it web-zecontinha sh

bash-dev:
	docker exec -it dev-zecontinha bash && docker exec -it dev-zecontinha sh

bash-cron:
	docker exec -it cron-zecontinha sh

bash-db:
	docker exec -it db-zecontinha sh

# ----------------------------
#        CRON COMMANDS
# ----------------------------

cron-calc:
	docker exec cron-zecontinha cron_calc

cron-calc-b3:
	docker exec cron-zecontinha cron_calc b3

cron-calc-binance:
	docker exec cron-zecontinha cron_calc binance

# ----------------------------
#        DJANGO HELPERS
# ----------------------------

migrate:
	docker exec -it web-zecontinha python /src/bin/manage.py migrate

makemigrations:
	docker exec -it web-zecontinha python /src/bin/manage.py makemigrations

shell:
	docker exec -it web-zecontinha python /src/bin/manage.py shell

collectstatic:
	docker exec -it web-zecontinha python /src/bin/manage.py collectstatic --noinput

# ----------------------------
#        CLEAN / RESET
# ----------------------------

clean:
	$(DOCKER_COMPOSE) down -v --remove-orphans

clean-all:
	docker system prune -af --volumes

# ----------------------------
#        HELP COMMAND
# ----------------------------

help:
	@echo "Available commands:"
	@echo "  build                 - Build all containers"
	@echo "  build-no-cache        - Build without cache"
	@echo "  up                    - Start production environment"
	@echo "  up-dev                - Start development environment"
	@echo "  up-db                 - Start only PostgreSQL"
	@echo "  up-cron               - Start only cron service"
	@echo "  down                  - Stop and remove all containers"
	@echo "  stop                  - Stop containers without removing"
	@echo "  restart               - Restart containers"
	@echo "  logs                  - Show logs from all services"
	@echo "  logs-app              - Show logs from app (production)"
	@echo "  logs-dev              - Show logs from app (dev)"
	@echo "  logs-db               - Show database logs"
	@echo "  logs-cron             - Show cron logs"
	@echo "  bash                  - Enter production app container"
	@echo "  bash-dev              - Enter dev container"
	@echo "  bash-cron             - Enter cron container"
	@echo "  bash-db               - Enter database container"
	@echo "  cron-calc             - Run cron_calc"
	@echo "  cron-calc-b3          - Run cron_calc b3"
	@echo "  cron-calc-binance     - Run cron_calc binance"
	@echo "  migrate               - Run Django migrations"
	@echo "  shell                 - Open Django shell"
	@echo "  collectstatic         - Run Django collectstatic"
	@echo "  clean                 - Remove containers and volumes"
	@echo "  clean-all             - Purge Docker system"
