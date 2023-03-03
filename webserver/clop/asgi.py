import os

os.environ.setdefault("DJANGO_SETTINGS_MODULE", "clop.config")
os.environ.setdefault("DJANGO_CONFIGURATION", "Development")

from configurations.asgi import get_asgi_application


application = get_asgi_application()
