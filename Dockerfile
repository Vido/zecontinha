# syntax=docker/dockerfile:1.4
FROM python:3.12-bookworm

ENV PYTHONPATH="/src/bin:/src" LANG=en_US.UTF-8 LANGUAGE=en_US.UTF-8 LC_ALL=en_US.UTF-8

WORKDIR /src
COPY ./poetry.lock ./pyproject.toml /src/

RUN DEBIAN_FRONTEND=noninteractive POETRY_VIRTUALENVS_CREATE=false && \
    apt-get update && \
    apt-get -y install cron busybox-syslogd locales \
        libnspr4 libnss3 libdbus-1-3 libatk1.0-0 libatk-bridge2.0-0 libatspi2.0-0 \
        libxcomposite1 libxdamage1 libxfixes3 libxrandr2 libgbm1 libxkbcommon0 libasound2 && \
    echo "en_US.UTF-8 UTF-8" >> /etc/locale.gen && locale-gen en_US.UTF-8 && \
    pip install --upgrade pip && \
    pip install poetry && \
    poetry config virtualenvs.create false && \
    poetry install --no-interaction --no-ansi --no-root && \
    playwright install && \
    apt-get remove --purge -y build-essential gcc g++ && \
    apt-get autoremove -y && \
    apt-get clean && rm -rf /var/lib/apt/lists/* && \
    pip cache purge
    # pip uninstall -y build-dependency

COPY ./cron.d/tasks-cron /etc/cron.d/tasks-cron
COPY ./src /src

RUN for f in /src/bin/*.py; do \
        base=$(basename "$f" .py); \
        ln -sf "$f" "/usr/local/bin/$base"; \
    done && \
    chmod +x /src/bin/*.py && \
    chmod 0644 /etc/cron.d/tasks-cron

ENTRYPOINT ["./bin/entrypoint.sh"]

CMD ["gunicorn", "vozdocu.wsgi", "-c", "vozdocu/gunicorn_conf.py"]
