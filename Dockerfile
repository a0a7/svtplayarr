FROM python:3.11-slim

# Install system dependencies
RUN apt-get update && apt-get install -y \
    git \
    curl \
    ffmpeg \
    gcc \
    g++ \
    python3-dev \
    build-essential \
    && rm -rf /var/lib/apt/lists/*

# Create app directory
WORKDIR /app

# Upgrade pip first
RUN pip install --upgrade pip

# Copy requirements first for better caching
COPY requirements.txt requirements-fallback.txt ./
RUN pip install --no-cache-dir -r requirements.txt || \
    (echo "Main requirements failed, trying fallback..." && \
     pip install --no-cache-dir -r requirements-fallback.txt)

# Install svtplay-dl from latest release
RUN pip install --no-cache-dir git+https://github.com/spaam/svtplay-dl.git

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
