#!/usr/bin/env bash
set -euo pipefail

[[ "${DEBUG:-0}" == "1" ]] && set -x

# Export all containers variables to a "container.env" file, then we load this file in "tasks-cron"
declare -p | grep -Ev 'BASHOPTS|BASH_VERSINFO|EUID|PPID|SHELLOPTS|UID' > /container.env

echo "Checking database"
python bin/check_db.py --service-name postgres --ip postgres --port 5432

echo "Running Django migrations..."
python manage.py migrate --noinput

echo "Entrypoint End"
exec "$@"
