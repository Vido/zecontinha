#!/usr/bin/env bash
set -euo pipefail

[[ "${DEBUG:-0}" == "True" ]] && set -x

# Development mode
#if [[ "${ENV:-}" == "development" ]]; then
if [[ "${DEBUG:-0}" == "True" ]]; then
    echo "Starting DEVELOPMENT server"
    exec manage runserver 0.0.0.0:8000
    # bypasses the default CMD
fi

echo "Running Django collectstatics..."
manage collectstatic --noinput

echo "Entrypoint End"
exec "$@"
