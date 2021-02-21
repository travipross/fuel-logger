#!/bin/sh

flask db upgrade -d fuel_logger/migrations

exech gunicorn --chdir fuel_logger fuel_logger:app
