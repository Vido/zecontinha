#!/usr/bin/env bash
set -euo pipefail

[[ "${DEBUG:-0}" == "1" ]] && set -x

echo "Checking database"
python bin/check_db.py --service-name postgres --ip postgres --port 5432

echo "Running Django migrations..."
python manage.py migrate --noinput

echo "Running Django collectstatics..."
python manage.py collectstatic --noinput

# Development mode
if [[ "${ENV:-}" == "development" ]]; then
    echo "Starting DEVELOPMENT server"
    exec python manage.py runserver 0.0.0.0:8000
    # bypasses the default CMD
fi

# Export all containers variables to a "container.env" file, then we load this file in "tasks-cron"
declare -p | grep -Ev 'BASHOPTS|BASH_VERSINFO|EUID|PPID|SHELLOPTS|UID' > /container.env

# Prepare log files and start outputting logs to stdout
mkdir -p /srv/logs/

echo "Entrypoint End"
exec "$@"
