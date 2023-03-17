from django.db import models


class NationResourceManager(models.Manager):
    def get_queryset(self):
        return super().get_queryset().filter(item_type__model='resource')


class NationBuildingManager(models.Manager):
    def get_queryset(self):
        return super().get_queryset().filter(item_type__model='building')
