import json

from django.core.exceptions import ImproperlyConfigured

from .base import *

with open('/home/pi/.configs/secret.json') as f:
    configs = json.loads(f.read())


def get_env_var(setting, configs=configs):
    try:
        val = configs[setting]
        if val == 'True':
            val = True
        elif val == 'False':
            val = False
        return val
    except KeyError:
        error_msg = "ImproperlyConfigured: Set {0} environment      variable".format(setting)
        raise ImproperlyConfigured(error_msg)


SECRET_KEY = get_env_var("SECRET_KEY")
DEBUG = True

ALLOWED_HOSTS = ['192.168.1.157', 'rpi-tijs.duckdns.org', 'raspberry']


DATABASES = {
    'default': {
        'ENGINE': 'django.db.backends.sqlite3',
        'NAME': os.path.join(BASE_DIR, 'db.sqlite3'),
    }
}

STATIC_URL = '/static/'
STATIC_ROOT = os.path.join(BASE_DIR, 'static/')
