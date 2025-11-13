FROM python:3.13-slim-bookworm

# Install uv.
COPY --from=ghcr.io/astral-sh/uv:latest /uv /uvx /bin/

# Copy the application into the container.
COPY . /app

# Install the application dependencies.
WORKDIR /app
RUN uv sync --frozen --no-cache --no-dev

# Install curl (needed for dotenvx installer) and TLS certs, then clean up
RUN apt-get update \
  && apt-get install -y --no-install-recommends curl ca-certificates \
  && rm -rf /var/lib/apt/lists/*

# Install dotenvx
RUN curl -sfS https://dotenvx.sh/install.sh | sh

# Run the application.
CMD ["dotenvx", "run", "--", "/app/.venv/bin/uvicorn", "src.main:app", "--host", "0.0.0.0", "--port", "8000", "--workers", "4"]
