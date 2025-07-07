#!/bin/bash

# SVTPlayArr startup script

echo "Starting SVTPlayArr..."

# Check if config exists, create if not
if [ ! -f /config/config.yml ]; then
    echo "Creating default configuration..."
    mkdir -p /config
    cp /app/config/config.yml /config/config.yml
fi

# Update svtplay-dl on startup
echo "Updating svtplay-dl..."
pip install --upgrade git+https://github.com/spaam/svtplay-dl.git

# Start the application
echo "Starting application..."
exec python /app/app.py
