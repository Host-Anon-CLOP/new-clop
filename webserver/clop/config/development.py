import mimetypes
from .common import Common, BASE_DIR


class Development(Common):
    DEBUG = True

    INSTALLED_APPS = Common.INSTALLED_APPS + [
        'debug_toolbar',
    ]

    # Mail
    EMAIL_HOST = 'localhost'
    EMAIL_PORT = 1025
    EMAIL_BACKEND = 'django.core.mail.backends.console.EmailBackend'

    MIDDLEWARE = [
        'debug_toolbar.middleware.DebugToolbarMiddleware',
    ] + Common.MIDDLEWARE

    INTERNAL_IPS = [
        '127.0.0.1',
    ]

    # Debug toolbar
    DEBUG_TOOLBAR_CONFIG = {
        'SHOW_TOOLBAR_CALLBACK': lambda request: True,
    }

    # Toolbar fix
    mimetypes.add_type("application/javascript", ".js", True)
