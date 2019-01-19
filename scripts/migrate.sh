#!/usr/bin/env bash
echo "---------- start migrate -------------"


cd /home/ec2-user/rest-api-server

pwd
python -V

python3 manage.py makemigrations
python3 manage.py migrate

python3 -m venv deployenv
source deployenv/bin/activate

python -V
pwd
/home/ec2-user/.local/bin/gunicorn --daemon -c gunicorn.conf rest_api_project.wsgi:application --log-file -
# /home/ec2-user/.local/bin/gunicorn  -c gunicorn.conf rest_api_project.wsgi:application --log-file -

echo "---------- finish migrate -------------"
# source /home/ec2-user/www/project-venv/bin/activate
# DJANGO_SETTINGS_MODULE=project.settings.staging \
# SECRET_KEY=your-secret-here \
# JWT_SECRET_KEY=your-jwt-secret-here \
# PSQL_DB_NAME=your-db-name-here \
# PSQL_DB_USER=your-db-user-here \
# PSQL_DB_PASSWD=your-db-password-here \
# PSQL_HOST=your-aws-psql-rds-server-dns-here \
# PSQL_PORT=5432 \
# ./manage.py makemigrations
#
#
# DJANGO_SETTINGS_MODULE=project.settings.staging SECRET_KEY=your-secret-here JWT_SECRET_KEY=your-jwt-secret-here PSQL_DB_NAME=your-db-name-here PSQL_DB_USER=your-db-user-here PSQL_DB_PASSWD=your-db-password-here PSQL_HOST=your-aws-psql-rds-server-dns-here PSQL_PORT=5432 ./manage.py migrate auth
#
#
# DJANGO_SETTINGS_MODULE=project.settings.staging SECRET_KEY=your-secret-here JWT_SECRET_KEY=your-jwt-secret-here PSQL_DB_NAME=your-db-name-here PSQL_DB_USER=your-db-user-here PSQL_DB_PASSWD=your-db-password-here PSQL_HOST=your-aws-psql-rds-server-dns-here PSQL_PORT=5432 ./manage.py migrate
