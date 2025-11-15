# syntax=docker/dockerfile:1.4
FROM python:3.12-bookworm

# Cron
# Add crontab file in the cron directory
ADD ./cron.d/tasks-cron /etc/cron.d/tasks-cron
# Give execution rights on the cron job
RUN chmod 0644 /etc/cron.d/tasks-cron
# Create the log file to be able to run tail
RUN touch /var/log/cron.log

# Install Cron
RUN DEBIAN_FRONTEND=noninteractive apt-get update && \
    apt-get -y install cron && \
    pip install --upgrade pip

# # Run the command on container startup
# RUN cron && tail -f /var/log/cron.log

WORKDIR /src
ADD ./ /src

# POETRY
ENV POETRY_VIRTUALENVS_CREATE=false
RUN pip install poetry && \
    poetry config virtualenvs.create false && \
    poetry install --no-interaction --no-ansi --no-root

# SEC hardening
RUN DEBIAN_FRONTEND=noninteractive apt-get remove --purge -y build-essential g++ && \
	apt-get autoremove -y && \
	apt-get clean && rm -rf /var/lib/apt/lists/* && \
	pip cache purge
	# pip uninstall -y build-dependency

ENTRYPOINT ["./bin/entrypoint.sh"]

CMD ["gunicorn", "vozdocu.wsgi", "-c", "vozdocu/gunicorn_conf.py"]
