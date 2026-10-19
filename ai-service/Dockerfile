# API-only is the default target. Build --target gpu for Pangu inference.
FROM python:3.11-slim-bookworm AS base

ENV PYTHONDONTWRITEBYTECODE=1 \
    PYTHONUNBUFFERED=1 \
    PIP_DISABLE_PIP_VERSION_CHECK=1 \
    PANGU_DATA_DIR=/app/data \
    PANGU_STATIONS_CSV=/app/stations.csv

WORKDIR /app
COPY requirements-api.txt ./
RUN python -m pip install --no-cache-dir -r requirements-api.txt
COPY pangu_service/ ./pangu_service/
COPY stations.csv ./

FROM base AS gpu
RUN apt-get update \
    && apt-get install -y --no-install-recommends libgomp1 \
    && rm -rf /var/lib/apt/lists/*
COPY requirements-pipeline.txt requirements-gpu-cuda12.txt ./
RUN python -m pip install --no-cache-dir \
    -r requirements-pipeline.txt -r requirements-gpu-cuda12.txt
CMD ["python", "-m", "pangu_service.auto_update"]

FROM base AS api
EXPOSE 8000
CMD ["python", "-m", "uvicorn", "pangu_service.api:app", "--host", "0.0.0.0", "--port", "8000"]
