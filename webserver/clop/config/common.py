import os
import logging
from pathlib import Path


import environ
from configurations import Configuration

logging.basicConfig()
logger = logging.getLogger(__name__)

BASE_DIR = Path(__file__).resolve().parent.parent
env = environ.Env()


def get_secret_file(key, default=env.NOTSET):
    path = Path(env(key, default=default))
    if path.exists():
        with path.open('r') as f:
            value = f.read().strip()
        return value
    elif default:
        return default
    else:
        logger.critical('Could not load secret from file!')
        return None


class Common(Configuration):
    INSTALLED_APPS = [
        # Django
        'django.contrib.admin',
        'django.contrib.auth',
        'django.contrib.contenttypes',
        'django.contrib.sessions',
        'django.contrib.messages',
        'django.contrib.staticfiles',
        # 'django.contrib.sites',

        # External
        'webpack_boilerplate',
        'django_extensions',

        # Internal
        'apps.users',
        'apps.nations'
    ]

    MIDDLEWARE = [
        'django.middleware.security.SecurityMiddleware',
        'django.contrib.sessions.middleware.SessionMiddleware',
        'django.middleware.common.CommonMiddleware',
        'django.middleware.csrf.CsrfViewMiddleware',
        'django.contrib.auth.middleware.AuthenticationMiddleware',
        'django.contrib.messages.middleware.MessageMiddleware',
        'django.middleware.clickjacking.XFrameOptionsMiddleware',
    ]

    DOMAIN_NAME = env('DOMAIN_NAME', default='clop.localhost')
    ALLOWED_HOSTS = [DOMAIN_NAME]
    CSRF_TRUSTED_ORIGINS = [f'https://*.{DOMAIN_NAME}']

    ROOT_URLCONF = 'clop.urls'
    SECRET_KEY = get_secret_file("DJANGO_SECRET_KEY_FILE")
    WSGI_APPLICATION = 'clop.wsgi.application'

    # SITE_ID = 1

    APPEND_SLASH = False
    TIME_ZONE = 'UTC'
    LANGUAGE_CODE = 'en'

    USE_I18N = True
    USE_L10N = True
    USE_TZ = True

    LOGIN_REDIRECT_URL = '/'
    LOGOUT_REDIRECT_URL = '/'

    AUTH_USER_MODEL = 'users.User'
    ACCOUNT_EMAIL_REQUIRED = False

    DATABASES = {
        'default': {
            'ENGINE': env('DB_ENGINE', default='django.db.backends.postgresql'),
            'NAME': env('DB_NAME', default='store'),
            'USER': env('DB_USER', default='postgres'),
            'PASSWORD': get_secret_file('POSTGRES_PASS_FILE'),
            'HOST': env('DB_HOST', default='127.0.0.1'),
            'PORT': env('DB_PORT', default=5432, cast=int),
        }
    }

    # Static files (CSS, JavaScript, Images)
    STATIC_URL = '/static/'
    STATIC_ROOT = BASE_DIR.parent.parent / 'staticfiles'
    STATICFILES_DIRS = (
        BASE_DIR.parent / 'static',
        BASE_DIR.parent / 'frontend/build',
    )

    MEDIA_URL = '/media/'
    MEDIA_ROOT = (BASE_DIR.parent.parent / 'media')

    FILE_UPLOAD_HANDLERS = [
        'django.core.files.uploadhandler.TemporaryFileUploadHandler',
    ]

    WEBPACK_LOADER = {
        'MANIFEST_FILE': BASE_DIR.parent / "frontend/build/manifest.json",
    }

    TEMPLATES = [
        {
            'BACKEND': 'django.template.backends.django.DjangoTemplates',
            'DIRS': (BASE_DIR.parent / 'templates',),
            'APP_DIRS': True,
            'OPTIONS': {
                'context_processors': [
                    'django.template.context_processors.debug',
                    'django.template.context_processors.request',
                    'django.contrib.auth.context_processors.auth',
                    'django.contrib.messages.context_processors.messages',
                ],
            },
        },
    ]

    # Password Validation
    AUTH_PASSWORD_VALIDATORS = [
        {
            'NAME': 'django.contrib.auth.password_validation.UserAttributeSimilarityValidator',
        },
        {
            'NAME': 'django.contrib.auth.password_validation.MinimumLengthValidator',
        },
        {
            'NAME': 'django.contrib.auth.password_validation.CommonPasswordValidator',
        },
        {
            'NAME': 'django.contrib.auth.password_validation.NumericPasswordValidator',
        },
    ]

    # Logging
    LOGGING = {
        'version': 1,
        'disable_existing_loggers': False,
        'formatters': {
            'django.server': {
                '()': 'django.utils.log.ServerFormatter',
                'format': '[%(server_time)s] %(message)s',
            },
            'verbose': {
                'format': '%(levelname)s %(asctime)s %(module)s %(process)d %(thread)d %(message)s'
            },
            'simple': {
                'format': '%(levelname)s %(message)s'
            },
        },
        'filters': {
            'require_debug_true': {
                '()': 'django.utils.log.RequireDebugTrue',
            },
        },
        'handlers': {
            'django.server': {
                'level': 'INFO',
                'class': 'logging.StreamHandler',
                'formatter': 'django.server',
            },
            'console': {
                'level': 'DEBUG',
                'class': 'logging.StreamHandler',
                'formatter': 'simple'
            },
            'mail_admins': {
                'level': 'ERROR',
                'class': 'django.utils.log.AdminEmailHandler'
            }
        },
        'loggers': {
            'django': {
                'handlers': ['console'],
                'propagate': True,
            },
            'django.server': {
                'handlers': ['django.server'],
                'level': 'INFO',
                'propagate': False,
            },
            'django.request': {
                'handlers': ['mail_admins', 'console'],
                'level': 'ERROR',
                'propagate': False,
            },
            'django.db.backends': {
                'handlers': ['console'],
                'level': 'INFO'
            },
        }
    }

