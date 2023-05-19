#!/bin/bash

pushed=false

if [[ -z "$DOCKER_REGISTRY" ]]; then
	echo "Must set \$DOCKER_REGISTRY to publish image."
	exit 1
fi

CONTAINER_NAME="fuel-logger"
IMAGE="${DOCKER_REGISTRY}/${CONTAINER_NAME}"


if [[ ! -z "${VERSION}" ]]; then
	docker tag "dev.local/${CONTAINER_NAME}:latest" "${IMAGE}:${VERSION}"
	docker push "${IMAGE}:${VERSION}"
	echo "Pushed ${IMAGE}:${VERSION}."
	pushed=true
fi

if [[ "${GITHUB_REF}" = "refs/heads/master" ]]; then
	TAG=latest
else
	TAG=dev
	echo "GITHUB_REF=${GITHUB_REF}"
fi

docker tag "dev.local/${CONTAINER_NAME}:latest" "${IMAGE}:${TAG}"
docker push "${IMAGE}:${TAG}"
echo "Pushed ${IMAGE}:${TAG}."
