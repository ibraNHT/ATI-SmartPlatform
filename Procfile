web: gunicorn src.Ati_smart_platform.wsgi:application --pythonpath ./src --log-file -
release: python manage.py migrate && python manage.py collectstatic --noinput