"""
WSGI config for electricreservation project.

It exposes the WSGI callable as a module-level variable named ``application``.

For more information on this file, see
https://docs.djangoproject.com/en/2.2/howto/deployment/wsgi/
"""

import os
import sys

from django.core.wsgi import get_wsgi_application

os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'electricreservation.settings.production')
sys.path.append('/home/pi/electricreservation')
sys.path.append('/home/pi/electricreservation/electricreservation')

application = get_wsgi_application()
