# OpenDSS FastAPI — reproducible runtime (Python slim + pinned install path).
# Build: docker build -t opendss-backend .
# Run:  docker run --rm -p 8000:8000 opendss-backend
# From host, point Nuxt at: NUXT_PUBLIC_API_BASE=http://127.0.0.1:8000
#
# Production: set ENVIRONMENT=production and CORS_ORIGINS to your frontend origin(s).
FROM python:3.12-slim

ENV PYTHONUNBUFFERED=1 \
    PIP_NO_CACHE_DIR=1 \
    PIP_DISABLE_PIP_VERSION_CHECK=1

RUN useradd --create-home --uid 1000 --shell /usr/sbin/nologin appuser

WORKDIR /app

COPY requirements.txt .
RUN pip install --no-cache-dir -r requirements.txt

COPY --chown=appuser:appuser app ./app

USER appuser

EXPOSE 8000

CMD ["uvicorn", "app.main:app", "--host", "0.0.0.0", "--port", "8000"]
