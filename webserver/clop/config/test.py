from .common import BASE_DIR, Common


class Test(Common):
    DEBUG = True

    # Mail
    EMAIL_HOST = 'localhost'
    EMAIL_PORT = 1025
    EMAIL_BACKEND = 'django.core.mail.backends.console.EmailBackend'
