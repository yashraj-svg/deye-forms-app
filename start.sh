#!/bin/bash
# Start script for Railway deployment
python manage.py migrate
gunicorn deye_config.wsgi:application --bind 0.0.0.0:$PORT
