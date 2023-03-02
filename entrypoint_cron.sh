#!/bin/bash
echo "Running Django migrations..."
python manage.py migrate --noinput

cron && tail -f /var/log/cron.log

echo "Entrypoint End"
exec $@