import json

from django.core.exceptions import ImproperlyConfigured

from .base import *

with open('secret.json') as f:
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
DEBUG = False

ALLOWED_HOSTS = ['rpi-tijs.duckdns.org']
