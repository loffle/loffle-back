from json import loads

from .base import *

STATIC_ROOT = BASE_DIR / 'static'
STATICFILES_DIRS = [
]

with open(BASE_DIR / 'secrets.json', 'r') as f:
    SECRETS = loads(f.read())

SECRET_KEY = SECRETS['SECRET_KEY']

EMAIL_HOST_USER = SECRETS['EMAIL_HOST_USER']
EMAIL_HOST_PASSWORD = SECRETS['EMAIL_HOST_PASSWORD']


if 'RDS_HOSTNAME' in SECRETS:
    DATABASES = {
        'default': {
            'ENGINE': 'django.db.backends.mysql',
            'NAME': SECRETS['RDS_DB_NAME'],
            'USER': SECRETS['RDS_USERNAME'],
            'PASSWORD': SECRETS['RDS_PASSWORD'],
            'HOST': SECRETS['RDS_HOSTNAME'],
            'PORT': SECRETS['RDS_PORT'],
            'OPTIONS': {
                'init_command': "SET sql_mode='STRICT_TRANS_TABLES'",
            }
        }
    }