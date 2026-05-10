# ── Stage 1: Build Vue.js frontend ──────────────────────────────────────────
FROM node:20-slim AS frontend-build

WORKDIR /app/frontend
COPY frontend/package.json frontend/pnpm-lock.yaml* ./
RUN npm install -g pnpm && pnpm install
COPY frontend/ ./
RUN pnpm run build

# ── Stage 2: Python backend + serve frontend static ──────────────────────────
FROM python:3.12-slim

# libpq-dev: cần cho psycopg2 (PostgreSQL driver)
RUN apt-get update && apt-get install -y --no-install-recommends \
    libpq-dev \
    && rm -rf /var/lib/apt/lists/*

WORKDIR /app

# Cài backend dependencies trước (tận dụng Docker layer cache)
COPY backend/requirements.txt ./backend/
RUN pip install --no-cache-dir -r backend/requirements.txt

# Copy source code backend
COPY backend/ ./backend/

# Copy frontend build từ Stage 1
COPY --from=frontend-build /app/frontend/dist ./frontend/dist

EXPOSE $PORT

WORKDIR /app/backend
CMD flask db upgrade && gunicorn run:app --bind 0.0.0.0:$PORT --workers 1
