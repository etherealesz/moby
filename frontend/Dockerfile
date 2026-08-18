FROM oven/bun:1.2.21-alpine AS base

RUN addgroup --gid 1001 --system bunjs && \
    adduser --system --uid 1001 --ingroup bunjs appuser

WORKDIR /app

# Copy common dir
COPY --chown=appuser:bunjs ./scripts ./scripts/
COPY --chown=appuser:bunjs ./public ./public/

# ===========================================================================
# Note:
# Below is the target to build, please enabled Docker BuildKit by setting
# DOCKER_BUILDKIT=1 in environment variable, then give the build command
# an argument to choose which target to be build.
# ===========================================================================

# ========================================
# Development only stage
# ========================================
FROM base AS development

# Copy standalone server file
COPY --chown=appuser:bunjs ./dist/development/standalone/server.js ./development-server.js

# Copy standalone dist dir
COPY --chown=appuser:bunjs ./dist/development/standalone/dist ./dist

# Copy static dir
COPY --chown=appuser:bunjs ./dist/development/static/ ./dist/development/static/

# Copy node modules
COPY --chown=appuser:bunjs ./dist/development/standalone/node_modules/ ./node_modules/

USER appuser

ENTRYPOINT [ "sh", "./scripts/start.sh" ]

# ========================================
# Staging and Production stage
# ========================================
FROM base AS staging-production

# Copy standalone server file
COPY --chown=appuser:bunjs ./dist/staging/standalone/server.js ./staging-server.js
COPY --chown=appuser:bunjs ./dist/production/standalone/server.js ./production-server.js

# Copy standalone dist dir
COPY --chown=appuser:bunjs ./dist/staging/standalone/dist ./dist
COPY --chown=appuser:bunjs ./dist/production/standalone/dist ./dist

# Copy static dir
COPY --chown=appuser:bunjs ./dist/staging/static/ ./dist/staging/static/
COPY --chown=appuser:bunjs ./dist/production/static/ ./dist/production/static/

# Copy node modules
COPY --chown=appuser:bunjs ./dist/production/standalone/node_modules/ ./node_modules/

USER appuser

ENTRYPOINT [ "sh", "./scripts/start.sh" ]
