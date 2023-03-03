from .common import Common, BASE_DIR


class Production(Common):
    DEBUG = False

    ADMINS = (
        ('Author', 'artem30801@gmail.com'),
    )

