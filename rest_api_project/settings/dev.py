
from .common import *
import os


DEBUG = True

# Database
# https://docs.djangoproject.com/en/2.0/ref/settings/#databases

DATABASES = {
    'default': {
        'ENGINE': 'django.db.backends.sqlite3',
        'NAME': os.path.join(BASE_DIR, 'db.sqlite3'),
    }
}

# static_path = os.environ.get('HOME')
# STATIC_ROOT = os.path.join(static_path, 'django_static')
STATIC_URL = '/static/'

MEDIA_ROOT = os.path.join(BASE_DIR, 'image')
MEDIA_URL = '/image/'


MIDDLEWARE += (
    'silk.middleware.SilkyMiddleware',
)

INSTALLED_APPS += (
    'silk',
)
