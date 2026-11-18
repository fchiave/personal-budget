COMPOSE := docker compose -p budget_devcontainer -f .devcontainer/docker-compose.yml -f .devcontainer/docker-compose.override.yml

.PHONY: up down status clean

# Wake up the existing dev container created by Zed
up:
	$(COMPOSE) start

# Stop the dev container when finished working
down:
	$(COMPOSE) stop

# Check if the container is currently running or stopped
status:
	$(COMPOSE) ps -a

# Remove the container and its associated images before rebuilding in Zed
clean:
	$(COMPOSE) down --rmi local --remove-orphans
	docker image prune -f
