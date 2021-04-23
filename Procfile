release: sh release-tasks.sh
web: cd original_sin  && gunicorn original_sin.wsgi --preload --log-level debug --enable-stdio-inheritance
worker: cd original_sin && python manage.py run_huey