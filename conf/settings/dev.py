from conf.settings.prod import INSTALLED_APPS, MIDDLEWARE, BASE_DIR, env


"""
START SITE APPS
"""

APPS = [
    "debug_toolbar",
    "querycount",
]

INSTALLED_APPS += APPS

"""
END SITE APPS

START DJANGO DEBUG TOOLBAR
"""

INTERNAL_IPS = [
    "127.0.0.1",
]  # for debug toolbar

"""
END DJANGO DEBUG TOOLBAR

START QUERY COUNTER
"""

QUERYCOUNT = {
    "THRESHOLDS": {"MEDIUM": 50, "HIGH": 200, "MIN_TIME_TO_LOG": 0, "MIN_QUERY_COUNT_TO_LOG": 0},
    "IGNORE_REQUEST_PATTERNS": [],
    "IGNORE_SQL_PATTERNS": [],
    "DISPLAY_DUPLICATES": None,
    "RESPONSE_HEADER": "X-DjangoQueryCount-Count",
}

"""
END QUERY COUNTER

START MIDDLEWARE
"""

MIDDLEWARE += [
    "querycount.middleware.QueryCountMiddleware",  # remove production
    "debug_toolbar.middleware.DebugToolbarMiddleware",  # remove production
]

"""
END MIDDLEWARE

START LOGGING
"""


LOGGING = {
    "version": 1,
    "disable_existing_loggers": False,
    "formatters": {
        "console": {"format": "%(message)s"},
        "db_requests": {
            "format": "%(asctime)s - [%(levelname)s] - %(message)s",
            "datefmt": "%Y-%m-%d %H:%M:%S",
        },
        "http_requests": {
            "format": "%(asctime)s - [%(levelname)s] - %(message)s",
            "datefmt": "%Y-%m-%d %H:%M:%S",
        },
    },
    "handlers": {
        "console": {"class": "logging.StreamHandler", "formatter": "console"},
        "db_request_error": {
            "class": "logging.handlers.TimedRotatingFileHandler",
            "filename": BASE_DIR / "logs/db_error.log",
            "formatter": "db_requests",
            "when": "D",
            "backupCount": 20,
            # 'maxBytes': 1024 * 1024 * 10,
        },
        "http_request_error": {
            "level": "WARNING",
            "class": "logging.handlers.TimedRotatingFileHandler",
            "filename": BASE_DIR / "logs/http_error.log",
            "formatter": "http_requests",
            "when": "D",
            "backupCount": 20,
        },
        "http_request_success": {
            "level": "DEBUG",
            "class": "logging.handlers.TimedRotatingFileHandler",
            "filename": BASE_DIR / "logs/http_success.log",
            "formatter": "http_requests",
            "when": "D",
            "backupCount": 20,
        },
    },
    "loggers": {
        "django.request": {
            "level": "DEBUG",
            "handlers": ["http_request_error", "http_request_success"]
            # 'handlers': ['console', 'http_request_error', 'http_request_success']
        },
        # "django.db.backends": {"level": "WARNING", "handlers": ["db_request_error"]},
        "django.db.backends": {"level": "DEBUG", "handlers": ["db_request_error", "console"]},
    },
}


"""
END LOGGING
"""
