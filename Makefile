# SVTPlayArr Makefile

.PHONY: help build test run stop clean publish publish-dockerhub publish-ghcr publish-both

# Default target
help:
	@echo "SVTPlayArr Build Commands:"
	@echo "  build            - Build Docker image locally"
	@echo "  test             - Build and run test environment"
	@echo "  run              - Run with docker-compose"
	@echo "  stop             - Stop all containers"
	@echo "  clean            - Remove containers and images"
	@echo "  publish-dockerhub - Build and publish to Docker Hub only"
	@echo "  publish-ghcr     - Build and publish to GitHub Container Registry only"
	@echo "  publish-both     - Build and publish to both registries"
	@echo "  logs             - Show container logs"

# Build the Docker image
build:
	docker build -t svtplayarr:latest .

# Build and run test environment
test:
	docker-compose -f docker-compose.test.yml up -d --build
	@echo "Test environment started on http://localhost:2626"
	@echo "Check logs with: make logs-test"

# Run production environment
run:
	@if [ ! -f .env ]; then \
		echo "Creating .env from template..."; \
		cp .env.example .env; \
		echo "Please edit .env with your configuration before running again"; \
		exit 1; \
	fi
	docker-compose up -d --build

# Stop containers
stop:
	docker-compose down
	docker-compose -f docker-compose.test.yml down

# Clean up containers and images
clean:
	docker-compose down -v --remove-orphans
	docker-compose -f docker-compose.test.yml down -v --remove-orphans
	docker image rm svtplayarr:latest 2>/dev/null || true

# Show logs
logs:
	docker-compose logs -f svtplayarr

logs-test:
	docker-compose -f docker-compose.test.yml logs -f svtplayarr

# Build and publish to Docker Hub only
publish-dockerhub:
	@read -p "Enter Docker Hub username: " username; \
	chmod +x build.sh; \
	./build.sh latest $$username

# Build and publish to GitHub Container Registry only  
publish-ghcr:
	@read -p "Enter GitHub username: " username; \
	chmod +x build.sh; \
	./build.sh latest "" $$username

# Build and publish to both registries
publish-both:
	@read -p "Enter Docker Hub username: " dockerhub; \
	read -p "Enter GitHub username: " github; \
	chmod +x build.sh; \
	./build.sh latest $$dockerhub $$github

# Legacy publish command (Docker Hub only for backward compatibility)
publish: publish-dockerhub

# Build multi-platform for Docker Hub
build-multiplatform-dockerhub:
	@read -p "Enter Docker Hub username: " username; \
	docker buildx build \
		--platform linux/amd64,linux/arm64,linux/arm/v7 \
		--tag $$username/svtplayarr:latest \
		--push .

# Build multi-platform for GitHub Container Registry
build-multiplatform-ghcr:
	@read -p "Enter GitHub username: " username; \
	docker buildx build \
		--platform linux/amd64,linux/arm64,linux/arm/v7 \
		--tag ghcr.io/$$username/svtplayarr:latest \
		--push .

# Check health
health:
	curl -f http://localhost:2626/health || echo "Service not healthy"

# Test webhook
test-webhook:
	curl -X POST http://localhost:2626/webhook \
		-H "Content-Type: application/json" \
		-d '{"media":{"title":"Test Show","mediaType":"tv"}}'
