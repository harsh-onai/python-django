FROM python:3.7-alpine
MAINTAINER OakNorth India Ltd

ENV PYTHONUNBUFFERED 1

COPY ./requirments.txt /requirments.txt

RUN apk add --update --no-cache postgresql-client
RUN apk add --update --no-cache --virtual .tmp-build-deps \
       gcc libc-dev linux-headers postgresql-dev
RUN pip install -r /requirments.txt  --trusted-host pypi.org --trusted-host files.pythonhosted.org
RUN apk del .tmp-build-deps

RUN mkdir /app
WORKDIR /app
COPY ./app /app

RUN adduser -D app-user
USER app-user