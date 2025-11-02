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

# Remove HEALTHCHECK - Railway handles health checks via HTTP probes
# HEALTHCHECK removed to avoid port conflicts with Railway's dynamic PORT

# Railway will use startCommand from railway.json
# Fallback CMD that uses PORT env variable
CMD sh -c "gunicorn -w 2 -b 0.0.0.0:\${PORT:-8000} --timeout 120 --keep-alive 2 app:app"
