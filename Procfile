

web: gunicorn hng_stage1.wsgi --log-file -
web: python manage.py migrate && gunicorn hng_stage1.wsgi 