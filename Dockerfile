FROM python:3.12-slim

# Install uv.
COPY --from=ghcr.io/astral-sh/uv:latest /uv /uvx /bin/

# Copy the application into the container.
COPY . /app

# Install the application dependencies.
WORKDIR /app
RUN uv sync --frozen --no-cache

# Install curl (needed for dotenvx installer) and TLS certs, then clean up
RUN apt-get update \
  && apt-get install -y --no-install-recommends curl ca-certificates \
  && rm -rf /var/lib/apt/lists/*

# Install dotenvx
RUN curl -sfS https://dotenvx.sh/install.sh | sh

# Run the application.
CMD ["dotenvx", "run", "-f", ".env.production", "--", "/app/.venv/bin/fastapi", "run", "src/main.py", "--port", "80", "--host", "0.0.0.0"]