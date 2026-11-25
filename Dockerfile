FROM python:3.14-slim
COPY --from=ghcr.io/astral-sh/uv:0.13.1 /uv /bin/uv

WORKDIR /app

# Install locked dependencies first, so this layer stays cached until uv.lock changes
COPY pyproject.toml uv.lock ./
RUN uv sync --frozen --no-dev
ENV PATH="/app/.venv/bin:$PATH"

# Copy the rest of the application
COPY app/utils/ ./utils/
COPY app/sync.py .

# Run python script periodically every hour
CMD ["bash", "-c", "while true; do python -u sync.py; echo 'Sleeping for 1 hour...'; sleep 3600; done"]
