# Use the official lightweight Python image
FROM python:3.10-slim

# Install Git
RUN apt-get update && apt-get install -y git \
    && rm -rf /var/lib/apt/lists/*

# Create a non-root user matching your local Ubuntu UID/GID (1000)
ARG USERNAME=devuser
ARG USER_UID=1000
ARG USER_GID=$USER_UID

RUN groupadd --gid $USER_GID $USERNAME \
    && useradd --uid $USER_UID --gid $USER_GID -m -s /bin/bash $USERNAME

# Set the working directory and give ownership to devuser
WORKDIR /workspace
RUN chown -R $USER_UID:$USER_GID /workspace

# Copy and install Python dependencies first for better layer caching
#COPY --chown=$USER_UID:$USER_GID requirements.txt .
#RUN pip install --no-cache-dir -r requirements.txt

# Copy the rest of the project files with proper ownership
COPY --chown=$USER_UID:$USER_GID . .

# Switch to the non-root user
USER $USERNAME

# Start a shell for interactive use
CMD ["/bin/bash"]
