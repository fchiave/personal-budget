# Use the official lightweight Python image
FROM python:3.12-slim

# Copy the official uv binary
COPY --from=ghcr.io/astral-sh/uv:latest /uv /bin/

# Install Git
RUN apt-get update && apt-get install -y git \
    && rm -rf /var/lib/apt/lists/*

# Create a non-root user matching your local Ubuntu UID/GID (1000)
ARG USERNAME=devuser
ARG USER_UID=1000
ARG USER_GID=$USER_UID

RUN groupadd --gid $USER_GID $USERNAME \
    && useradd --uid $USER_UID --gid $USER_GID -m -s /bin/bash $USERNAME

# Store venv in devuser's home dir (already owned by devuser, outside /workspace)
ENV UV_PROJECT_ENVIRONMENT=/home/devuser/.venv
ENV PATH="/home/devuser/.venv/bin:$PATH"

WORKDIR /workspace
RUN chown $USER_UID:$USER_GID /workspace

# Switch to the non-root user before installing dependencies
USER $USERNAME

# Copy dependency definitions first for Docker layer caching
COPY --chown=$USER_UID:$USER_GID pyproject.toml uv.lock* ./
RUN uv sync --no-install-project

# Keep the container alive for dev container attachment
CMD ["sleep", "infinity"]
