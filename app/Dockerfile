FROM python:3-alpine

RUN pip3 install gunicorn flask Flask-Limiter requests mysql-connector-python 
RUN apk add mariadb mariadb-client

COPY src /app

WORKDIR /app

COPY entrypoint.sh /entrypoint.sh
ENTRYPOINT ["/entrypoint.sh"]
