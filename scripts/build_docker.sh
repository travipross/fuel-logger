#!/bin/bash

if [[ -z "$DOCKER_REGISTRY" ]]; then
	echo "You must provide a \$DOCKER_REGISTRY in order to build and tag"
	exit 1
fi

BASENAME=fuel-logger

docker build \
	-t "${DOCKER_REGISTRY}/${BASENAME}:local" \
	.

echo "Built image for ${DOCKER_REGISTRY}/${BASENAME}:local."
