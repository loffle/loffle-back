from .base import *

DEBUG = False

ALLOWED_HOSTS = [
    '127.0.0.1',
    'Loffleback-env.us-west-2.elasticbeanstalk.com',
]

STATIC_ROOT = BASE_DIR / 'static'
STATICFILES_DIRS = [
]