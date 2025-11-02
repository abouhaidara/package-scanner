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

# ---- Runtime config ----
ENV FLASK_ENV=production \
    PYTHONPATH=/app

# Expose default port (Railway will override with PORT env var)
EXPOSE 8000

# Health check - Railway provides PORT at runtime
HEALTHCHECK --interval=30s --timeout=30s --start-period=5s --retries=3 \
  CMD curl -fsS http://localhost:8000/health || exit 1

# Use Railway's startCommand from railway.json, or fallback to this
# Railway will use the startCommand from railway.json, so this is just a fallback
CMD ["gunicorn", "-w", "4", "-b", "0.0.0.0:8000", "--timeout", "120", "--keep-alive", "2", "--max-requests", "1000", "--max-requests-jitter", "100", "app:app"]
