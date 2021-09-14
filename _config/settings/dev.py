from json import loads

from .base import *

with open(BASE_DIR / 'secrets.json', 'r') as f:
    SECRETS = loads(f.read())

SECRET_KEY = SECRETS['SECRET_KEY']

STATIC_ROOT = BASE_DIR / 'static'
STATICFILES_DIRS = [
]