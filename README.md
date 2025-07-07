# svtplayarr
*arr stack integration for SVT Play and NRK (Swedish and Norwegian public broadcaster streaming services)

## Overview

svtplayarr is a service that integrates the SVT Play and NRK (Swedish and Norwegian public broadcaster) streaming services with your Jellyfin *arr stack. When content is requested through Jellyseerr and is available on SVT Play or NRK, it will be automatically downloaded using svtplay-dl.

## Features

- Automatic content detection on SVT Play and NRK
- Integration with Jellyseerr webhooks
- Full svtplay-dl configuration support
- Automatic Sonarr/Radarr notification after download
- Daily updates of svtplay-dl from GitHub releases
- RESTful API for manual operations
- Configurable download settings

## Installing

### Docker Compose: 

Chose a container registry: 

**Docker Hub:**
```yaml
services:
  svtplayarr:
    image: username/svtplayarr:latest
    # ... rest of configuration
```

**GitHub Container Registry:**
```yaml
services:
  svtplayarr:
    image: ghcr.io/username/svtplayarr:latest
    # ... rest of configuration
```

## Quick Start

1. Copy the environment file:
   ```bash
   cp .env.example .env
   ```

2. Edit `.env` with your *arr stack configuration:
   ```bash
   # Required
   JELLYSEERR_API_KEY=your_api_key
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

4. Configure Jellyseerr webhook (see Webhook Setup section below)

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
| `JELLYSEERR_API_KEY` | Jellyseerr API key | Required |
| `JELLYSEERR_URL` | Jellyseerr URL | `http://jellyseerr:5055` |
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
Jellyseerr webhook endpoint

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
      - JELLYSEERR_API_KEY=your_key
      - SONARR_API_KEY=your_key
      - RADARR_API_KEY=your_key
    networks:
      - arr-network

networks:
  arr-network:
    external: true
```

## Jellyseerr Webhook Setup

The webhook URL depends on your Docker setup:

### Scenario 1: All services in same Docker Compose network (Recommended)
1. Go to Jellyseerr Settings → Notifications
2. Add a new Webhook notification
3. Set URL to: `http://svtplayarr:2626/webhook`
4. Enable for "Media Requested" events
5. Set request types to both Movies and TV Shows

### Scenario 2: Jellyseerr on host, svtplayarr in Docker
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
- *arr stack (Jellyseerr, Sonarr, Radarr)
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