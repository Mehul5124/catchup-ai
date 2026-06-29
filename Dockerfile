# ────────────────────────────────────────────────────────────────────────────
#  CatchUp AI – Dockerfile
#  Builds a container that runs the Streamlit dashboard on port 8502
# ────────────────────────────────────────────────────────────────────────────

FROM python:3.12-slim

# --------------------------------------------------------------------------
# System deps
# --------------------------------------------------------------------------
RUN apt-get update && apt-get install -y --no-install-recommends \
        build-essential \
        curl \
    && rm -rf /var/lib/apt/lists/*

# --------------------------------------------------------------------------
# Working directory
# --------------------------------------------------------------------------
WORKDIR /app

# --------------------------------------------------------------------------
# Install Python dependencies (layer-cached before copying source)
# --------------------------------------------------------------------------
COPY requirements.txt .
RUN pip install --no-cache-dir --upgrade pip \
 && pip install --no-cache-dir -r requirements.txt

# --------------------------------------------------------------------------
# Copy source code
# --------------------------------------------------------------------------
COPY . .

# --------------------------------------------------------------------------
# Environment defaults (override at runtime with -e or --env-file)
# --------------------------------------------------------------------------
ENV CATCHUP_MODE=mock
ENV PYTHONUNBUFFERED=1
ENV PYTHONDONTWRITEBYTECODE=1

# --------------------------------------------------------------------------
# Expose port
#   8502 – Streamlit UI  (matches README and run command)
# --------------------------------------------------------------------------
EXPOSE 8502

# --------------------------------------------------------------------------
# Health check
# --------------------------------------------------------------------------
HEALTHCHECK --interval=30s --timeout=10s --start-period=15s --retries=3 \
    CMD curl -f http://localhost:8502/_stcore/health || exit 1

# --------------------------------------------------------------------------
# Entry point – Streamlit UI
# --------------------------------------------------------------------------
ENTRYPOINT ["streamlit", "run", "app.py", \
            "--server.port=8502", \
            "--server.address=0.0.0.0", \
            "--server.headless=true", \
            "--browser.gatherUsageStats=false"]