#!/bin/bash
cd /src/zecontinha

echo "Running Django migrations..."
python manage.py migrate --noinput

echo "Running Django collectstatics..."
python manage.py collectstatic --noinput

echo "Starting server"
python manage.py runserver 0.0.0.0:8000

echo "Entrypoint End"
exec $@