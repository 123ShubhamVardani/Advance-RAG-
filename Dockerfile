# Multi-stage build for Streamlit AI Chatbot
# 1. Base builder installs dependencies
# 2. Slim runtime with only needed packages

ARG PYTHON_VERSION=3.12-slim
FROM python:${PYTHON_VERSION} AS base

# Prevent Python from writing pyc files and buffering stdout
ENV PYTHONDONTWRITEBYTECODE=1 \
    PYTHONUNBUFFERED=1

WORKDIR /app

# System deps (add as needed)
RUN apt-get update && apt-get install -y --no-install-recommends \
    build-essential \
    curl \
    && rm -rf /var/lib/apt/lists/*

# Copy dependency files first (better layer caching)
COPY pyproject.toml requirements.txt* setup.py ./

# Install dependencies (prefer wheels, disable cache)
RUN pip install --upgrade pip && \
    if [ -f requirements.txt ]; then pip install --no-cache-dir -r requirements.txt; fi

# Copy application
COPY . .

# Expose Streamlit default port
EXPOSE 8501

# Environment defaults (override at runtime)
ENV CONNECTION_TEST_TIMEOUT=5 \
    CONNECTION_TEST_RETRIES=2 \
    CONNECTION_TEST_BACKOFF=0.5 \
    AUTO_OFFLINE_FAIL_THRESHOLD=3 \
    PYTHONPATH=/app

# Health check: simple import check
HEALTHCHECK --interval=60s --timeout=5s --retries=3 CMD python -c "import importlib; import sys; sys.exit(0 if importlib.util.find_spec('streamlit') else 1)"

# Run the Streamlit app
CMD ["streamlit", "run", "app.py", "--server.port=8501", "--server.address=0.0.0.0"]
