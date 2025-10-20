web: gunicorn string_analyzer.wsgi --log-file -
web: python manage.py migrate && gunicorn string_analyzer.wsgi
