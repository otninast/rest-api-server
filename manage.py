#!/usr/bin/env python
import os
import sys
import pymysql
pymysql.install_as_MySQLdb()

if __name__ == "__main__":
    # os.environ.setdefault("DJANGO_SETTINGS_MODULE", "rest_api_project.settings.prod")
    if os.environ.get('RDS_USER'):
        os.environ.setdefault("DJANGO_SETTINGS_MODULE", "rest_api_project.settings.prod")
    else:
        os.environ.setdefault("DJANGO_SETTINGS_MODULE", "rest_api_project.settings.dev")

    try:
        from django.core.management import execute_from_command_line
    except ImportError as exc:
        raise ImportError(
            "Couldn't import Django. Are you sure it's installed and "
            "available on your PYTHONPATH environment variable? Did you "
            "forget to activate a virtual environment?"
        ) from exc
    execute_from_command_line(sys.argv)
