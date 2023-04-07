from .common import BASE_DIR, Common


class Development(Common):
    DEBUG = True

    # INSTALLED_APPS = Common.INSTALLED_APPS + [
    #
    # ]

    # Mail
    EMAIL_HOST = 'localhost'
    EMAIL_PORT = 1025
    EMAIL_BACKEND = 'django.core.mail.backends.console.EmailBackend'

    # MIDDLEWARE = [
    #
    # ] + Common.MIDDLEWARE

    # Debug toolbar
    DEBUG_TOOLBAR_CONFIG = {
        'SHOW_TOOLBAR_CALLBACK': lambda request: True,
    }
