release: sh release-tasks.sh
web: cd original_sin  && gunicorn original_sin.wsgi --preload --access-logfile '-'
worker: cd original_sin && python manage.py run_huey