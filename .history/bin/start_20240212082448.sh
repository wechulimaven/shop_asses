#!/bin/bash

set -e  # Configure shell so that if one command fails, it exits

# python manage.py makemigrations
python manage.py migrate

flake8
# python manage.py test
# coverage erase
# coverage run manage.py test
# coverage report
# python manage.py runserver 0.0.0.0:8000
gunicorn shop.wsgi:application --bind 0.0.0.0:8000 --timeout 120 --workers 2 --log-level info
