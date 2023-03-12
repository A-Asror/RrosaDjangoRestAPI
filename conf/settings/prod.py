import os
from pathlib import Path

import environ

env = environ.Env()
env.read_env(".env")

BASE_DIR = Path(__file__).resolve().parent.parent.parent

SECRET_KEY = env.str("SECRET_KEY")

DEBUG = env.bool("DEBUG", False)

ALLOWED_HOSTS = ["*"]

INSTALLED_APPS = [
    "django.contrib.admin",
    "django.contrib.auth",
    "django.contrib.contenttypes",
    "django.contrib.sessions",
    "django.contrib.messages",
    "django.contrib.staticfiles",
    "rest_framework",

    "src.users",
    # "corsheaders",  # DJANGO-CORS_HEADERS
    # "django_celery_beat",  # DJANGO-CELERY-BEAT
]

MIDDLEWARE = [
    "django.middleware.security.SecurityMiddleware",
    "django.contrib.sessions.middleware.SessionMiddleware",
    "django.middleware.common.CommonMiddleware",
    "django.middleware.csrf.CsrfViewMiddleware",
    "django.contrib.auth.middleware.AuthenticationMiddleware",
    "django.contrib.messages.middleware.MessageMiddleware",
    "django.middleware.clickjacking.XFrameOptionsMiddleware",
    # "corsheaders.middleware.CorsMiddleware",  # DJANGO-CORS_HEADERS
]

ROOT_URLCONF = "conf.urls"

TEMPLATES = [
    {
        "BACKEND": "django.template.backends.django.DjangoTemplates",
        "DIRS": [os.path.join(BASE_DIR, "templates")],
        "APP_DIRS": True,
        "OPTIONS": {
            "context_processors": [
                "django.template.context_processors.debug",
                "django.template.context_processors.request",
                "django.contrib.auth.context_processors.auth",
                "django.contrib.messages.context_processors.messages",
            ],
        },
    },
]

WSGI_APPLICATION = "conf.wsgi.application"

DATABASES = {
    # SQLITE
    "default": {
        "ENGINE": "django.db.backends.sqlite3",
        "NAME": BASE_DIR / "db.sqlite3",
        **env.dict("DB_OTHER_DATA")  # DB Other Settings
    }
    # POSTGRES, MARIADB, MYSQL.
    # "default": {
    #     "ENGINE": env.str("DB_ENGINE", ""),
    #     "NAME": env.str("DB_NAME", ""),
    #     "USER": env.str("DB_USER", ""),
    #     "PASSWORD": env.str("DB_PASSWORD", ""),
    #     "HOST": env.str("DB_HOST", ""),
    #     "PORT": env.int("DB_PORT", ""),
    #     **env.dict("DB_OTHER_DATA"),
    # },
}

AUTH_PASSWORD_VALIDATORS = [
    {
        "NAME": "django.contrib.auth.password_validation.UserAttributeSimilarityValidator",
    },
    {
        "NAME": "django.contrib.auth.password_validation.MinimumLengthValidator",
    },
    {
        "NAME": "django.contrib.auth.password_validation.CommonPasswordValidator",
    },
    {
        "NAME": "django.contrib.auth.password_validation.NumericPasswordValidator",
    },
]

LANGUAGE_CODE = "en-us"

TIME_ZONE = "Asia/Tashkent"

USE_I18N = True

USE_L10N = True

USE_TZ = True

STATIC_URL = "/static/"

STATICFILES_DIRS = (os.path.join(BASE_DIR, "static"),)
STATIC_ROOT = os.path.join(BASE_DIR, "staticfiles")

MEDIA_ROOT = os.path.join(BASE_DIR, "media")
MEDIA_URL = "/media/"


"""
START SITE APPS
"""

MY_APPS = [
    # "src.users"  # Example
]

INSTALLED_APPS += MY_APPS

"""
END SITE APPS
"""


REST_FRAMEWORK = {
    'DEFAULT_PERMISSION_CLASSES': ['rest_framework.permissions.AllowAny'],
    'EXCEPTION_HANDLER': 'rest_framework.views.exception_handler',
    'DEFAULT_AUTHENTICATION_CLASSES': ['src.utils.authentication.JWTAuthentication']
}


"""
START DJANGO REDIS CONF
"""

# CACHES = {
#     "default": {
#         "BACKEND": env.str("BACKEND"),
#         "LOCATION": env.str("LOCATION"),
#         "OPTIONS": env.dict("OPTIONS"),
#     }
# }

CACHE_TTL = 60 * 15

"""
END DJANGO REDIS CONF

START CELERY CONF
"""

# CELERY_BROKER_URL = env.str("CELERY_BROKER_URL")
# CELERY_RESULT_BACKEND = env.str("CELERY_RESULT_BACKEND")
# CELERY_ACCEPT_CONTENT = ["application/json"]
# CELERY_TASK_SERIALIZER = "json"
# CELERY_RESULT_SERIALIZER = "json"
# CELERY_TASK_TRACK_STARTED = True
# CELERY_TASK_TIME_LIMIT = 30 * 60

# DJANGO CELERY BEAT
# CELERY_BEAT_SCHEDULER = "django_celery_beat.schedulers:DatabaseScheduler"

"""
END CELERY CONF

START CORS SETTINGS
"""

CORS_ALLOW_CREDENTIALS = True
CORS_ORIGIN_ALLOW_ALL = True

CORS_ORIGIN_WHITELIST = ("http://localhost:3000",)

"""
END CORS SETTINGS

START EMAIL SETTINGS
"""

# EMAIL_BACKEND = env.str("EMAIL_BACKEND")
# EMAIL_HOST = env.str("EMAIL_HOST")
# EMAIL_PORT = env.int("EMAIL_PORT")
# EMAIL_USE_TLS = env.bool("EMAIL_USE_TLS")
# EMAIL_HOST_USER = env.str("EMAIL_HOST_USER")
# EMAIL_HOST_PASSWORD = env.str("EMAIL_HOST_PASSWORD")

"""
END EMAIL SETTINGS

START CHANNELS
"""

# ASGI_APPLICATION = "conf.asgi.application"
#
# CHANNEL_LAYERS = {
#     "default": {
#         "BACKEND": "channels_redis.core.RedisChannelLayer",
#         "CONFIG": {
#             "hosts": [("127.0.0.1", 6379)],
#         },
#     }
# }

"""
END CHANNELS

START Site Domains
"""

DOMAIN_FRONT_END = env.str("DOMAIN_FRONT_END")
DOMAIN_BACK_END = env.str("DOMAIN_BACK_END")


"""
END Site Domains

START OTHER SETTINGS
"""

# AUTH_USER_MODEL = "users.UserModel"


"""
END OTHER SETTINGS
"""


try:
    if DEBUG is True:
        from conf.settings.dev import *  # TODO python:S2208
except ImportError:
    pass
