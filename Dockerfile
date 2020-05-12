FROM python:3.7-alpine
MAINTAINER OakNorth India Ltd

ENV PYTHONUNBUFFERED 1

COPY ./requirments.txt /requirments.txt

RUN pip install -r /requirments.txt  --trusted-host pypi.org --trusted-host files.pythonhosted.org

RUN mkdir /app
WORKDIR /app
COPY ./app /app

RUN adduser -D app-user
USER app-user