#!/usr/bin/env bash
set -euo pipefail

[[ "${DEBUG:-0}" == "1" ]] && set -x

printenv \
  | grep -Ev '^(PWD|OLDPWD|HOME|HOSTNAME|TERM|SHLVL|_)=.*' \
  | sed 's/^/export /' \
  | sort \
  > /etc/environment

syslogd -n -O /proc/1/fd/1 &

echo "Checking database"
python bin/check_db.py --service-name postgres --ip postgres --port 5432

echo "Running Django migrations..."
python manage.py migrate --noinput

echo "Entrypoint End"
exec "$@"
