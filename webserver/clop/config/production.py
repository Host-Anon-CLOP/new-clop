from .common import BASE_DIR, Common


class Production(Common):
    DEBUG = False

    ADMINS = (
        ('Author', 'artem30801@gmail.com'),
    )

