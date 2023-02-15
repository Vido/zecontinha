# syntax=docker/dockerfile:1.4
FROM python:3.6.15-buster

WORKDIR /src
ADD ./ /src

RUN pip install install --upgrade pip
RUN pip3 install -r requirements.txt

ENTRYPOINT ["./entrypoint.sh"]

EXPOSE 8000