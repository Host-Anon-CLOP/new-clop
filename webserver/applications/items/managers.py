from django.db import models


class BundleManager(models.Manager):
    def get_queryset(self):
        return super().get_queryset().prefetch_related('items')


class BundleItemManager(models.Manager):
    def get_queryset(self):
        return super().get_queryset().prefetch_related('item')


class RecipeManager(models.Manager):
    def get_queryset(self):
        return super().get_queryset().select_related('produces', 'consumes').prefetch_related('produces__items', 'consumes__items')


class BuildingManager(models.Manager):
    def get_queryset(self):
        return super().get_queryset().select_related('produces', 'consumes').prefetch_related('produces__items', 'consumes__items')
