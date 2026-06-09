web: python manage.py collectstatic --noinput && python manage.py migrate --noinput && gunicorn evaluation_system.wsgi:application --bind 0.0.0.0:8000
