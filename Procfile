release: sh release-tasks.sh
web: cd original_sin  && gunicorn original_sin.wsgi --preload --log-level debug
worker: cd original_sin && python manage.py run_huey