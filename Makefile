COMPOSE := docker compose -p budget_devcontainer -f .devcontainer/docker-compose.yml -f .devcontainer/docker-compose.override.yml

.PHONY: up down status

# Wake up the existing dev container created by Zed
up:
	$(COMPOSE) start

# Stop the dev container when finished working
down:
	$(COMPOSE) stop

# Check if the container is currently running or stopped
status:
	$(COMPOSE) ps -a
