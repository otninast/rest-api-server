
from .common import *

DEBUG = True

# Database
# https://docs.djangoproject.com/en/2.0/ref/settings/#databases

DATABASES = {
    'default': {
        'ENGINE': 'django.db.backends.sqlite3',
        'NAME': os.path.join(BASE_DIR, 'db.sqlite3'),
    }
}

STATIC_URL = '/static/'

MEDIA_ROOT = os.path.join(BASE_DIR, 'image')
MEDIA_URL = '/image/'


MIDDLEWARE += (
    'silk.middleware.SilkyMiddleware',
)

INSTALLED_APPS += (
    'silk',
)
