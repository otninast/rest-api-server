#!/usr/bin/env bash
echo "---------- start migrate -------------"

source /home/ec2-user/.bash_profile

cd /home/ec2-user/rest-api-server
# python3 manage.py cllectstatic
python3 manage.py makemigrations
python3 manage.py migrate
# sudo chmod +w /home/ec2-user/rest-api-server
sudo chown ec2-user:ec2-user ~/rest-api-server
python3 -m venv deployenv
# sudo chmod +x /home/ec2-user/rest-api-server/deployenv/bin/activate
source deployenv/bin/activate

pkill -INT gunicorn
/home/ec2-user/.local/bin/gunicorn --daemon -c gunicorn.conf rest_api_project.wsgi:application --log-file -

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
