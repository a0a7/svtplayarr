# svtplayarr
*arr stack integration for SVT Play and NRK (Swedish and Norwegian public broadcaster streaming services)

## Overview

SVTPlayArr is a service that integrates SVT Play and NRK (the respective public broadcaster streaming services for Sweden and Norway) with your *arr stack. When content is requested through Jellyseerr or Overseerr and is available on SVT Play or NRK, it will be automatically downloaded using svtplay-dl.

## Features

- Automatic content detection on SVT Play and NRK
- Integration with Jellyseerr and Overseerr webhooks
- Full svtplay-dl configuration support
- Automatic Sonarr/Radarr notification after download
- Daily updates of svtplay-dl from GitHub releases
- RESTful API for manual operations
- Configurable download settingsrr stack integration for SVT Play and NRK (Swedish and Norwegian public broadcaster streaming services)

## Installing

### Docker Compose: 

Chose a container registry: 

**Docker Hub:**
```yaml
services:
  svtplayarr:
    image: username/svtplayarr:latest
    # ... rest of config
```

**GitHub Container Registry:**
```yaml
services:
  svtplayarr:
    image: ghcr.io/username/svtplayarr:latest
    # ... rest of config
```

## Quick Start

1. Copy the environment file:
   ```bash
   cp .env.example .env
   ```

2. Edit `.env` with your *arr stack configuration:
   ```bash
   # Required
   SONARR_API_KEY=your_api_key
   RADARR_API_KEY=your_api_key
   
   # Paths
   MOVIES_PATH=/path/to/movies
   TV_PATH=/path/to/tv
   ```

3. Start the service:
   ```bash
   docker-compose up -d
   ```

4. Configure Jellyseerr/Overseerr webhook (see Webhook Setup section below)

## Webhook URL Configuration

The webhook URL depends on your setup:

- **Docker Compose (same network)**: `http://svtplayarr:2626/webhook`
- **Docker with host networking**: `http://localhost:2626/webhook`
- **Different networks**: `http://<container-ip>:2626/webhook`
- **External Jellyseerr**: `http://<host-ip>:2626/webhook`

## Configuration

### Environment Variables

| Variable | Description | Default |
|----------|-------------|---------|
| `SONARR_API_KEY` | Sonarr API key | Required |
| `SONARR_URL` | Sonarr URL | `http://sonarr:8989` |
| `RADARR_API_KEY` | Radarr API key | Required |
| `RADARR_URL` | Radarr URL | `http://radarr:7878` |
| `MOVIES_PATH` | Movies download path | `/downloads/movies` |
| `TV_PATH` | TV shows download path | `/downloads/tv` |
| `LOG_LEVEL` | Logging level | `INFO` |

### SVTPlay-dl Options

svtplay-dl options are configurable via the `config/config.yml` file:

```yaml
svtplay_dl:
  quality: "best"          # Video quality
  subtitle: true           # Download subtitles
  force_subtitle: false    # Force subtitle download
  remux: false            # Remux to mkv
  merge_subtitle: false   # Merge subtitles into video
  thumbnail: false        # Download thumbnails
```

## API Endpoints

### GET /health
Health check endpoint

### POST /webhook
Jellyseerr/Overseerr webhook endpoint

### GET /webhook/test
Shows webhook format examples and test information

### GET /search?title=<title>&type=<tv|movie>
Search for content manually

### GET /config
Get current configuration

### POST /config
Update configuration

## Docker Compose Integration

```yaml
version: '3.8'

services:
  svtplayarr:
    build: .
    container_name: svtplayarr
    restart: unless-stopped
    ports:
      - "2626:2626"
    volumes:
      - ./config:/config
      - /path/to/movies:/downloads/movies
      - /path/to/tv:/downloads/tv
    environment:
      - SONARR_API_KEY=your_key
      - RADARR_API_KEY=your_key
    networks:
      - arr-network

networks:
  arr-network:
    external: true
```

## Jellyseerr/Overseerr Webhook Setup

The webhook URL depends on your Docker setup:

### Scenario 1: All services in same Docker Compose network (Recommended)
1. Go to Jellyseerr/Overseerr Settings → Notifications
2. Add a new Webhook notification
3. Set URL to: `http://svtplayarr:2626/webhook`
4. Enable for "Media Requested" events
5. Set request types to both Movies and TV Shows

### Scenario 2: Jellyseerr/Overseerr on host, SVTPlayArr in Docker
1. Use URL: `http://localhost:2626/webhook`
2. Ensure port 2626 is exposed (already configured in docker-compose.yml)

### Scenario 3: Different Docker networks
1. Use URL: `http://<host-ip>:2626/webhook` where `<host-ip>` is your Docker host IP
2. Alternative: Connect containers to same network

### Scenario 4: Testing webhook manually
```bash
curl -X POST http://localhost:2626/webhook \
  -H "Content-Type: application/json" \
  -d '{"media":{"title":"Example Show","mediaType":"tv"}}'
```


## Requirements

- Docker and Docker Compose
- *arr stack (Jellyseerr/Overseerr, Sonarr, Radarr)
- Network connectivity to Swedish/Norwegian streaming services

## Troubleshooting

### Logs
```bash
docker-compose logs -f svtplayarr
```

### Test Connection
```bash
curl http://localhost:2626/health
```

### Test Webhook Format
```bash
curl http://localhost:2626/webhook/test
```

### Manual Search
```bash
curl "http://localhost:2626/search?title=Example%20Show&type=tv"
```

## Building

### Local Build
```bash
# Build locally
make build

# Test locally
make test

# Run production
make run
```
