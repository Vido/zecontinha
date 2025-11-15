# syntax=docker/dockerfile:1.4
FROM python:3.12-bookworm

WORKDIR /src

ENV DEBIAN_FRONTEND=noninteractive
ENV POETRY_VIRTUALENVS_CREATE=false
ENV PYTHONPATH="/src/bin:${PYTHONPATH}"

# TODO: make a ./src in to store the project files
COPY ./ /src

RUN apt-get update && \
    apt-get -y install cron && \
    pip install --upgrade pip && \
    pip install poetry && \
    poetry config virtualenvs.create false && \
    poetry install --no-interaction --no-ansi --no-root && \
    apt-get remove --purge -y build-essential gcc g++ && \
    apt-get autoremove -y && \
    apt-get clean && rm -rf /var/lib/apt/lists/* && \
    pip cache purge
    # pip uninstall -y build-dependency


# Cron
RUN ln -sf /src/bin/cron_calc.py /usr/local/bin/cron_calc && \
    ln -sf /src/bin/bot.py /usr/local/bin/bot && \
    ln -sf /src/cron.d/tasks-cron /etc/cron.d/tasks-cron && \
    chmod +x /src/bin/*.py  && \
    chmod 0644 /etc/cron.d/tasks-cron && \
    touch /var/log/cron.log

ENTRYPOINT ["./bin/entrypoint.sh"]

CMD ["gunicorn", "vozdocu.wsgi", "-c", "vozdocu/gunicorn_conf.py"]
