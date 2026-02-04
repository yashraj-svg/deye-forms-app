#!/bin/bash
# Build script for Railway deployment
pip install --upgrade pip
pip install -r requirements.txt
python manage.py collectstatic --noinput
