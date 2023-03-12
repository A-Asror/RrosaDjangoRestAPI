# from __future__ import absolute_import, unicode_literals
#
# import os
#
# import environ
# from celery import Celery
# from django.apps import apps
# from django.conf import settings
#
# env = environ.Env()
# env.read_env(".env")
# os.environ.setdefault("DJANGO_SETTINGS_MODULE", env.str("DJANGO_SETTINGS_MODULE"))
#
# app = Celery("conf")
# app.config_from_object("django.conf:settings")
#
# app.config_from_object(settings)
# app.autodiscover_tasks(lambda: [app.name for app in apps.get_app_configs()])
#
# app.conf.update(enable_utc=True, timezone="Asia/Tashkent")
