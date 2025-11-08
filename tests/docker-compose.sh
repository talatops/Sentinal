#!/bin/bash
# Helper script to run docker compose with .docker.env file
# Usage: ./docker-compose.sh [docker compose commands...]

ENV_FILE=".docker.env"

if [ ! -f "$ENV_FILE" ]; then
    echo "Error: $ENV_FILE not found!"
    echo "Please copy .docker.env.example to .docker.env and configure it."
    exit 1
fi

docker compose --env-file "$ENV_FILE" "$@"

