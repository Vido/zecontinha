# syntax=docker/dockerfile:1.4
FROM python:3.7.16-buster


# Cron
# Add crontab file in the cron directory
ADD ./cron.d/crontab /etc/cron.d/crontab
# Give execution rights on the cron job
RUN chmod 0644 /etc/cron.d/crontab
# Create the log file to be able to run tail
RUN touch /var/log/cron.log
#Install Cron
RUN apt-get update
RUN apt-get -y install cron

# # Run the command on container startup
# RUN cron && tail -f /var/log/cron.log
ADD ./entrypoint_cron.sh ./entrypoint_cron.sh

WORKDIR /src
ADD ./ /src

RUN pip install install --upgrade pip
#RUN pip install -r requirements.txt

RUN pip install poetry
RUN poetry config virtualenvs.create false

RUN poetry install --no-interaction --no-ansi

ENTRYPOINT ["./entrypoint.sh"]

EXPOSE 8000