#!/bin/sh

flask db upgrade -d fuel_logger/migrations

gunicorn -b :${GUNICORN_PORT:-8000} --chdir fuel_logger fuel_logger:app
