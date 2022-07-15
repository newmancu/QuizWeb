#!/bin/bash

echo "Connecting to db..."

while ! nc -z ${DB_HOST} ${DB_PORT}; do
  sleep .2s
done

echo "Connected to DB"

python ./quizweb/manage.py makemigrations
python ./quizweb/manage.py migrate
python ./quizweb/manage.py base_conf

exec "$@"