#!/bin/bash

# SVTPlayArr startup script

echo "Starting SVTPlayArr..."

# Check if config exists, create if not
if [ ! -f /config/config.yml ]; then
    echo "Creating default configuration..."
    mkdir -p /config
    cp /app/config/config.yml /config/config.yml
fi

# Check if svtplay-dl is installed, install if not
if ! command -v svtplay-dl &> /dev/null; then
    echo "svtplay-dl not found, attempting installation..."
    pip install --no-cache-dir git+https://github.com/spaam/svtplay-dl.git || \
    pip install --no-cache-dir svtplay-dl || \
    echo "Warning: Could not install svtplay-dl - downloads may fail"
else
    echo "Updating svtplay-dl..."
    pip install --upgrade --no-cache-dir git+https://github.com/spaam/svtplay-dl.git || \
    pip install --upgrade --no-cache-dir svtplay-dl || \
    echo "Warning: Could not update svtplay-dl"
fi

# Start the application
echo "Starting application..."
exec python /app/app.py
