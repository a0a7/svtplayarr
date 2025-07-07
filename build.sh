#!/bin/bash

set -e

VERSION=${1:-latest}
DOCKER_USERNAME=${2:-""}
GITHUB_USERNAME=${3:-""}
IMAGE_NAME="svtplayarr"

# Determine registries to publish to
PUBLISH_DOCKERHUB=false
PUBLISH_GHCR=false

if [ -n "$DOCKER_USERNAME" ]; then
    PUBLISH_DOCKERHUB=true
    DOCKERHUB_IMAGE="${DOCKER_USERNAME}/${IMAGE_NAME}"
fi

if [ -n "$GITHUB_USERNAME" ]; then
    PUBLISH_GHCR=true
    GHCR_IMAGE="ghcr.io/${GITHUB_USERNAME}/${IMAGE_NAME}"
fi

echo "Building SVTPlayArr version: ${VERSION}"

# Check if buildx is available for multi-platform builds
if docker buildx version >/dev/null 2>&1; then
    echo "Docker Buildx detected - building multi-platform image"
    
    # Create builder if it doesn't exist
    docker buildx create --name svtplayarr-builder --use 2>/dev/null || docker buildx use svtplayarr-builder
    
    # Build tags array
    TAGS=""
    
    if [ "$PUBLISH_DOCKERHUB" = true ]; then
        TAGS="${TAGS} --tag ${DOCKERHUB_IMAGE}:${VERSION} --tag ${DOCKERHUB_IMAGE}:latest"
        echo "Will publish to Docker Hub: ${DOCKERHUB_IMAGE}"
    fi
    
    if [ "$PUBLISH_GHCR" = true ]; then
        TAGS="${TAGS} --tag ${GHCR_IMAGE}:${VERSION} --tag ${GHCR_IMAGE}:latest"
        echo "Will publish to GitHub Container Registry: ${GHCR_IMAGE}"
    fi
    
    if [ -n "$TAGS" ]; then
        # Build and push for multiple platforms
        docker buildx build \
            --platform linux/amd64,linux/arm64,linux/arm/v7 \
            ${TAGS} \
            --push \
            .
        echo "Multi-platform images built and pushed"
    else
        echo "No registries specified. Building local image only."
        docker buildx build \
            --platform linux/amd64 \
            --tag "${IMAGE_NAME}:${VERSION}" \
            --tag "${IMAGE_NAME}:latest" \
            --load \
            .
    fi
else
    echo "Building single platform image"
    
    # Build for current platform
    docker build -t "${IMAGE_NAME}:${VERSION}" -t "${IMAGE_NAME}:latest" .
    
    # Tag and push if requested
    if [ "$PUBLISH_DOCKERHUB" = true ]; then
        docker tag "${IMAGE_NAME}:${VERSION}" "${DOCKERHUB_IMAGE}:${VERSION}"
        docker tag "${IMAGE_NAME}:latest" "${DOCKERHUB_IMAGE}:latest"
        docker push "${DOCKERHUB_IMAGE}:${VERSION}"
        docker push "${DOCKERHUB_IMAGE}:latest"
        echo "Pushed to Docker Hub: ${DOCKERHUB_IMAGE}"
    fi
    
    if [ "$PUBLISH_GHCR" = true ]; then
        docker tag "${IMAGE_NAME}:${VERSION}" "${GHCR_IMAGE}:${VERSION}"
        docker tag "${IMAGE_NAME}:latest" "${GHCR_IMAGE}:latest"
        docker push "${GHCR_IMAGE}:${VERSION}"
        docker push "${GHCR_IMAGE}:latest"
        echo "Pushed to GitHub Container Registry: ${GHCR_IMAGE}"
    fi
    
    if [ "$PUBLISH_DOCKERHUB" = false ] && [ "$PUBLISH_GHCR" = false ]; then
        echo "Image built locally as ${IMAGE_NAME}:${VERSION}"
        echo "Usage: $0 <version> <docker-username> <github-username>"
    fi
fi

echo "Build completed"
