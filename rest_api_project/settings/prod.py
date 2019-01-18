from .common import *
import os

DEBUG = True

ALLOWED_HOSTS = ['*']


# Database
# https://docs.djangoproject.com/en/2.0/ref/settings/#databases

# DATABASES = {
#     'default': {
#         'ENGINE': 'django.db.backends.sqlite3',
#         'NAME': os.path.join(BASE_DIR, 'db.sqlite3'),
#     }
# }

DATABASES = {
    'default': {
        'ENGINE': 'django.db.backends.mysql',
        'NAME': 'restapidb',
        'USER': os.environ.get('RDS_USER'),
        'PASSWORD': os.environ.get('RDS_PASSWORD'),
        'HOST': os.environ.get('RDS_HOST'),
        'PORT': os.environ.get('RDS_PORT'),
    }
}

INSTALLED_APPS += (
    'gunicorn',
)

static_path = os.environ.get('HOME')
STATIC_ROOT = os.path.join(static_path, 'django_static')

STATIC_URL = '/static/'

MEDIA_ROOT = os.path.join(STATIC_ROOT, 'image')
MEDIA_URL = '/image/'
