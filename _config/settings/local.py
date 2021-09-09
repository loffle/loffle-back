from .base import *

with open(BASE_DIR / 'secrets.json', 'r') as f:
    SECRETS = loads(f.read())

SECRET_KEY = SECRETS['SECRET_KEY']