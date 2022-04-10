#!/bin/sh

cd original_sin || exit 1

echo 'db migrate'
python manage.py migrate

echo 'manage fix_default_admin'
python manage.py fix_default_admin
echo 'manage check_aws_s3'
python manage.py check_aws_s3
