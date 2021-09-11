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

        }
    }


def is_ec2_linux():
    """Detect if we are running on an EC2 Linux Instance
       See http://docs.aws.amazon.com/AWSEC2/latest/UserGuide/identify_ec2_instances.html
    """
    if os.path.isfile("/sys/hypervisor/uuid"):
        with open("/sys/hypervisor/uuid") as f:
            uuid = f.read()
            return uuid.startswith("ec2")
    return False


def get_linux_ec2_private_ip():
    """Get the private IP Address of the machine if running on an EC2 linux server"""
    import requests
    if not is_ec2_linux():
        return None
    try:
        response = requests.get('http://172.31.17.216/latest/meta-data/local-ipv4')
        return response.text
    except:
        return None


private_ip = get_linux_ec2_private_ip()
if private_ip:
    ALLOWED_HOSTS.append(private_ip)
