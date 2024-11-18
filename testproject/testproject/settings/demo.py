from .base import *  # noqa

DEBUG = os.environ.get("DJANGO_DEBUG", "") != "False"
ALLOWED_HOSTS = ["*"]
SESSION_COOKIE_DOMAIN = ".localhost"
SESSION_COOKIE_SECURE = True

MIDDLEWARE += ["testproject.middleware.DemoMiddleware"]
