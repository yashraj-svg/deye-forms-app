release: python manage.py migrate && python manage.py collectstatic --noinput
web: gunicorn deye_config.wsgi:application --bind 0.0.0.0:$PORT
