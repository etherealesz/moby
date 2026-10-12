FROM ghcr.io/astral-sh/uv:python3.11-bookworm-slim AS builder

ENV UV_LINK_MODE=copy
ENV UV_NO_CACHE=1
ENV UV_PYTHON_DOWNLOADS=0
ENV UV_NO_DEV=1
ENV UV_FROZEN=1

WORKDIR /app

COPY pyproject.toml uv.lock ./
RUN uv sync --no-install-project --group deployment

FROM python:3.11-slim-bookworm AS runtime

ENV PATH="/app/.venv/bin:$PATH"
ENV PYTHONPATH=".:/app/src"

WORKDIR /app

RUN apt-get update && \
    apt-get install -y --no-install-recommends libgl1 libglib2.0-0 && \
    rm -rf /var/lib/apt/lists/*

RUN groupadd --gid 1001 --system fastapi && \
    useradd --system --uid 1001 --gid fastapi appuser

COPY --chown=appuser:fastapi --from=builder /app/.venv .venv

COPY --chown=appuser:fastapi src src
COPY --chown=appuser:fastapi files files
COPY --chown=appuser:fastapi models models
COPY --chown=appuser:fastapi scripts/start.sh scripts/
COPY --chown=appuser:fastapi main.py .

EXPOSE 8080

USER appuser

CMD ["sh", "scripts/start.sh"]
