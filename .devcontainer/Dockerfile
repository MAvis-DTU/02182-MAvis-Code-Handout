FROM ghcr.io/mavis-dtu/02182-base:latest

# Set `DEVCONTAINER` environment variable to help with orientation
ENV DEVCONTAINER=true

# Install uv
RUN curl -LsSf https://astral.sh/uv/install.sh | sh
ENV PATH="/root/.local/bin:$PATH"
