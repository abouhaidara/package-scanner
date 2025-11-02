# ---- Base ----
    FROM python:3.9-slim

    # Keep apt non-interactive and Python tidy
    ENV DEBIAN_FRONTEND=noninteractive \
        PYTHONDONTWRITEBYTECODE=1 \
        PYTHONUNBUFFERED=1
    
    # System libs needed by OpenCV/Pillow + ffmpeg + healthcheck curl
    RUN apt-get update && apt-get install -y --no-install-recommends \
        curl \
        ffmpeg \
        libgl1 \
        libglib2.0-0 \
        libsm6 \
        libxext6 \
        libxrender1 \
        libgomp1 \
        libgtk-3-0 \
     && rm -rf /var/lib/apt/lists/*
    
    # ---- App setup ----
    WORKDIR /app
    
    # Faster, reproducible pip installs
    COPY requirements.txt .
    RUN python -m pip install --upgrade pip && \
        pip install --no-cache-dir -r requirements.txt && \
        pip install --no-cache-dir gunicorn
    
    # Copy source
    COPY . .
    
    # Ensure runtime dirs exist
    RUN mkdir -p uploads logs
    
    # (Optional) only if you truly need scripts executable
    # RUN chmod +x *.py || true
    
    # ---- Runtime config ----
    EXPOSE 8000
    ENV PORT=8000 \
        FLASK_ENV=production \
        PYTHONPATH=/app
    
    # Health check (needs curl installed above)
    HEALTHCHECK --interval=30s --timeout=30s --start-period=5s --retries=3 \
      CMD curl -fsS http://localhost:8000/health || exit 1
    
    # Gunicorn entrypoint (adjust module:app if different)
    CMD ["gunicorn", "-w", "4", "-b", "0.0.0.0:8000", "--timeout", "120", "--keep-alive", "2", "--max-requests", "1000", "--max-requests-jitter", "100", "app:app"]
    