#!/bin/bash

CONTAINER_NAME=fuel-logger

docker build \
	-t "dev.local/${CONTAINER_NAME}:latest" \
	.

echo "Built image for dev.local/${CONTAINER_NAME}:latest."
