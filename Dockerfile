# syntax=docker/dockerfile:1.4
FROM python:3.7.17-bullseye


# Cron
# Add crontab file in the cron directory
ADD ./cron.d/tasks-cron /etc/cron.d/tasks-cron
# Give execution rights on the cron job
RUN chmod 0644 /etc/cron.d/tasks-cron
# Create the log file to be able to run tail
RUN touch /var/log/cron.log
#Install Cron
RUN apt-get update
RUN apt-get -y install cron

# # Run the command on container startup
# RUN cron && tail -f /var/log/cron.log

WORKDIR /src
ADD ./ /src

RUN pip install install --upgrade pip

# POETRY
ENV POETRY_VIRTUALENVS_CREATE=false
RUN pip install poetry && \
    poetry config virtualenvs.create false
RUN poetry install --no-interaction --no-ansi
