#!/bin/sh

cd original_sin || exit 1

echo 'db migrate'
python manage.py migrate
echo 'db migrate old_bot_db'
python manage.py migrate --database=old_bot_db
echo 'db migrate postgresql'
python manage.py migrate --database=postgresql

echo 'manage fix_default_admin'
python manage.py fix_default_admin
echo 'manage check_aws_s3'
python manage.py check_aws_s3
