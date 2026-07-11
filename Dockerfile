# syntax=docker/dockerfile:1

FROM python:3.11-slim-bookworm

ENV PYTHONDONTWRITEBYTECODE=1 \
    PYTHONUNBUFFERED=1 \
    PIP_DISABLE_PIP_VERSION_CHECK=1 \
    PIP_NO_CACHE_DIR=1 \
    PORT=8000

WORKDIR /app

# Create an unprivileged runtime user.
RUN groupadd --system appuser \
    && useradd \
        --system \
        --gid appuser \
        --create-home \
        appuser

# Copy dependencies first to improve Docker layer caching.
COPY requirements.txt ./requirements.txt

RUN python -m pip install --upgrade pip setuptools wheel \
    && python -m pip install --prefer-binary -r requirements.txt

# Copy only the application files required at runtime.
COPY api ./api
COPY src ./src
COPY config.yaml ./config.yaml

# Make the directories explicit Python packages.
RUN touch api/__init__.py src/__init__.py \
    && chown -R appuser:appuser /app

USER appuser

# This compile check catches syntax errors during the image build.
RUN python -m compileall -q api src

# This import check prevents publishing an image that cannot start.
RUN python -c "from api.main import app; print(app.title)"

EXPOSE 8000

HEALTHCHECK --interval=30s --timeout=5s --start-period=10s --retries=3 \
    CMD python -c "import urllib.request; urllib.request.urlopen('http://127.0.0.1:8000/health', timeout=3)" || exit 1

CMD ["sh", "-c", "exec uvicorn api.main:app --host 0.0.0.0 --port ${PORT:-8000}"]
