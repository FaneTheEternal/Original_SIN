release: python manage.py migrate && python manage.py migrate --database=old_bot_db && python manage.py migrate --database=postgresql
web: cd original_sin  && gunicorn original_sin.wsgi --preload