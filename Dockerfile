FROM python:3.11-slim as builder

# Install build dependencies
RUN apt-get update && apt-get install -y \
    git \
    gcc \
    g++ \
    python3-dev \
    build-essential \
    libffi-dev \
    libssl-dev \
    cargo \
    rustc \
    pkg-config \
    && rm -rf /var/lib/apt/lists/*

# Upgrade pip
RUN pip install --upgrade pip

# Install Python dependencies
COPY requirements.txt requirements-fallback.txt ./
RUN pip install --no-cache-dir -r requirements.txt || \
    (echo "Main requirements failed, trying fallback..." && \
     pip install --no-cache-dir -r requirements-fallback.txt)

# Try to install svtplay-dl
RUN pip install --no-cache-dir git+https://github.com/spaam/svtplay-dl.git || \
    pip install --no-cache-dir svtplay-dl || \
    echo "Warning: svtplay-dl installation failed"

# Runtime stage
FROM python:3.11-slim

# Install only runtime dependencies
RUN apt-get update && apt-get install -y \
    curl \
    ffmpeg \
    && rm -rf /var/lib/apt/lists/*

# Copy Python packages from builder
COPY --from=builder /usr/local/lib/python3.11/site-packages /usr/local/lib/python3.11/site-packages
COPY --from=builder /usr/local/bin /usr/local/bin

# Create app directory
WORKDIR /app

# Copy application code
COPY . .

# Make startup script executable
RUN chmod +x startup.sh

# Create directories
RUN mkdir -p /downloads/movies /downloads/tv /config

# Expose port
EXPOSE 2626

# Health check
HEALTHCHECK --interval=30s --timeout=10s --start-period=5s --retries=3 \
    CMD curl -f http://localhost:2626/health || exit 1

# Run application
CMD ["./startup.sh"]
