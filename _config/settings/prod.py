import os

from .base import *

DEBUG = False

SECRET_KEY = os.environ['DJANGO_SECRET_KEY']

ALLOWED_HOSTS = [
    # '127.0.0.1',
    'loffle-back-dev.us-west-2.elasticbeanstalk.com',
    'loffle-back-prod.us-west-2.elasticbeanstalk.com',
    'loffle.cf',

]

STATIC_ROOT = BASE_DIR / 'static'
STATICFILES_DIRS = [
]

if 'RDS_HOSTNAME' in os.environ:
    DATABASES = {
        'default': {
            'ENGINE': 'django.db.backends.mysql',
            'NAME': os.environ['RDS_DB_NAME'],
            'USER': os.environ['RDS_USERNAME'],
            'PASSWORD': os.environ['RDS_PASSWORD'],
            'HOST': os.environ['RDS_HOSTNAME'],
            'PORT': os.environ['RDS_PORT'],
            'OPTIONS': {
                'init_command': "SET sql_mode='STRICT_TRANS_TABLES'",
            }
        }
    }

import socket
local_ip = str(socket.gethostbyname(socket.gethostname()))
ALLOWED_HOSTS.append(local_ip)

EMAIL_HOST_USER = os.environ['EMAIL_HOST_USER']
EMAIL_HOST_PASSWORD = os.environ['EMAIL_HOST_PASSWORD']
