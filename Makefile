COMPOSE := docker compose -p budget_devcontainer -f .devcontainer/docker-compose.yml -f .devcontainer/docker-compose.override.yml

.PHONY: up down status clean test lint format check sync

# - - - Container Lifecycle Commands - - -
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

# - - - Code Quality & Testing Commands - - -
# Run unit tests inside the dev container
test:
	$(COMPOSE) exec app pytest

# Check linting and formatting without modifying files
lint:
	$(COMPOSE) exec app ruff check .
	$(COMPOSE) exec app ruff format --check .

# Auto-fix lint issues and format Code
format:
	$(COMPOSE) exec app ruff check --fix .
	$(COMPOSE) exec app ruff format .

# Run full quality gate before comitting
check: lint test

# - - - Git Workflow Commands - - -
# Switch to dev, pull latest changes, prune stale remotes, and delete merged local branches
sync:
	git checkout dev
	git pull --ff-only origin dev
	git fetch --prune
	git branch -vv | awk '/: gone]/ && $$1 !~ /^(\*|main|dev)$$/ {print $$1}' | xargs -r git branch -D
