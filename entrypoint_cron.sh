#!/bin/bash

# Export all containers variables to a "container.env" file, then we load this file in "tasks-cron"
declare -p | grep -Ev 'BASHOPTS|BASH_VERSINFO|EUID|PPID|SHELLOPTS|UID' > /container.env

echo "Running Django migrations..."
python manage.py migrate --noinput

echo "Running Cron..."
cron && tail -f /var/log/cron.log

echo "Entrypoint End"
exec $@