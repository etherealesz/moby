# =========== Build Stage =========== #
FROM astral/uv:python3.14-alpine AS builder

# UV configuration environment variables.
ENV UV_LINK_MODE=copy
ENV UV_NO_CACHE=1
ENV UV_PYTHON_DOWNLOADS=0
ENV UV_NO_DEV=1
ENV UV_FROZEN=1

WORKDIR /app

# Install python dependencies
COPY pyproject.toml uv.lock ./
RUN uv sync --no-install-project --group deployment

# =========== Run Stage =========== #
FROM python:3.14-alpine AS runtime

# Python configuration environment variables.
ENV PATH="/app/.venv/bin:$PATH"
ENV PYTHONPATH=".:/app/src"

WORKDIR /app

RUN addgroup --gid 1001 --system fastapi && \
    adduser --system --uid 1001 --ingroup fastapi appuser

# Copy necessary files
COPY --chown=appuser:fastapi --from=builder /app/.venv .venv

COPY --chown=appuser:fastapi src src
COPY --chown=appuser:fastapi files files
COPY --chown=appuser:fastapi scripts/start.sh scripts/
COPY --chown=appuser:fastapi main.py .

EXPOSE 8080

USER appuser

CMD ["sh", "scripts/start.sh"]
