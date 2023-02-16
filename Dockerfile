# syntax=docker/dockerfile:1.4
FROM python:3.7.16-buster

WORKDIR /src
ADD ./ /src

RUN pip install install --upgrade pip
#RUN pip install -r requirements.txt

RUN pip install poetry
RUN poetry config virtualenvs.create false

RUN poetry install --no-interaction --no-ansi

ENTRYPOINT ["./entrypoint.sh"]

EXPOSE 8000