#!/usr/bin/env bash

cd cd /home/ec2-user/rest-api-server
gunicorn --daemon -c gunicorn.conf rest_api_project.wsgi:application --log-file -
