import os

import environ
from django.core.wsgi import get_wsgi_application

env = environ.Env()
env.read_env(".env")

os.environ.setdefault("DJANGO_SETTINGS_MODULE", env.str("DJANGO_SETTINGS_MODULE"))

application = get_wsgi_application()
