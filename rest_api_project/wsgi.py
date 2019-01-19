"""
WSGI config for rest_api_project project.

It exposes the WSGI callable as a module-level variable named ``application``.

For more information on this file, see
https://docs.djangoproject.com/en/2.0/howto/deployment/wsgi/
"""

import os
from django.core.wsgi import get_wsgi_application
import pymysql
pymysql.install_as_MySQLdb()

# os.environ.setdefault("DJANGO_SETTINGS_MODULE", "rest_api_project.settings.prod")
if os.environ.get('USER') == os.environ.get('DEPLOY_USER'):
    os.environ.setdefault("DJANGO_SETTINGS_MODULE", "rest_api_project.settings.prod")
else:
    os.environ.setdefault("DJANGO_SETTINGS_MODULE", "rest_api_project.settings.dev")

application = get_wsgi_application()
