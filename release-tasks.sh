#!/bin/sh

cd original_sin || exit 1
python manage.py migrate
python manage.py migrate --database=old_bot_db
python manage.py migrate --database=postgresql
python manage.py fix_default_admin
