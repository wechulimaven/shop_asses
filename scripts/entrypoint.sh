#!/bin/sh

set -e  # Configure shell so that if one command fails, it exits

python manage.py wait_for_db
python manage.py migrate
python manage.py create_super_user
# flake8

gunicorn shop.wsgi:application --bind 0.0.0.0:8000 --timeout 120 --workers 3
