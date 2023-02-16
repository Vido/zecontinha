#!/bin/bash
set -e

if [ -n "$1" ]; then
    exec "$@"
fi

echo "Running Django migrations..."
python manage.py migrate --noinput
echo "Running Django collectstatics..."
python manage.py collectstatic --noinput

if [ "$ENV" = "development" ] ; then
    echo "Starting server"
    python manage.py runserver 0.0.0.0:8000
else
    # Prepare log files and start outputting logs to stdout
    mkdir -p /srv/logs/
    touch /srv/logs/gunicorn.log
    touch /srv/logs/access.log
    tail -n 0 -f /srv/logs/*.log &

    # Start Gunicorn processes
    echo Starting Gunicorn
    exec gunicorn vozdocu.wsgi \
        --bind 0.0.0.0:8000 \
        --chdir /src \
        --workers 3 \
        --log-level=info \
        --log-file=/srv/logs/gunicorn.log \
        --access-logfile=/srv/logs/access.log
fi