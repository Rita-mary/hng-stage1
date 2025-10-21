web: gunicorn string_analyzer.wsgi --log-file -
web: python manage.py migrate && python manage.py collectstatic --noinput && gunicorn string_analyzer.wsgi
