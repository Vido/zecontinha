# syntax=docker/dockerfile:1.4
FROM python:3.12-bookworm

WORKDIR /src

ENV PYTHONPATH="/src/bin:/src"
ENV LANG=en_US.UTF-8 LANGUAGE=en_US.UTF-8 LC_ALL=en_US.UTF-8

# TODO: make a ./src in to store the project files
COPY ./ /src

RUN DEBIAN_FRONTEND=noninteractive POETRY_VIRTUALENVS_CREATE=false && \
    apt-get update && \
    apt-get -y install cron busybox-syslogd locales && \
    echo "en_US.UTF-8 UTF-8" >> /etc/locale.gen && locale-gen en_US.UTF-8 && \
    pip install --upgrade pip && \
    pip install poetry && \
    poetry config virtualenvs.create false && \
    poetry install --no-interaction --no-ansi --no-root && \
    apt-get remove --purge -y build-essential gcc g++ && \
    apt-get autoremove -y && \
    apt-get clean && rm -rf /var/lib/apt/lists/* && \
    pip cache purge
    # pip uninstall -y build-dependency


RUN for f in /src/bin/*.py; do \
        base=$(basename "$f" .py); \
        ln -sf "$f" "/usr/local/bin/$base"; \
    done && \
    chmod +x /src/bin/*.py && \
    ln -sf /src/cron.d/tasks-cron /etc/cron.d/tasks-cron && \
    chmod 0644 /etc/cron.d/tasks-cron

ENTRYPOINT ["./bin/entrypoint.sh"]

CMD ["gunicorn", "vozdocu.wsgi", "-c", "vozdocu/gunicorn_conf.py"]
