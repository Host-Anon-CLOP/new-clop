import functools

from django.contrib.contenttypes.models import ContentType
from django.core.cache import cache


def reset_cache():
    get_all_buildings.cache_clear()
    get_all_resources.cache_clear()
    get_all_recipes.cache_clear()
    get_all_items.cache_clear()


@functools.cache
def get_all_buildings():
    return cache.get('buildings')


@functools.cache
def get_all_resources():
    return cache.get('resources')


@functools.cache
def get_all_recipes():
    return cache.get('recipes')


@functools.cache
def get_all_items():
    from applications.items.models import Building, Resource

    resource_type = ContentType.objects.get_for_model(Resource).pk
    building_type = ContentType.objects.get_for_model(Building).pk

    resource_items = {(item_id, resource_type): item for item_id, item in get_all_resources().items()}
    building_items = {(item_id, building_type): item for item_id, item in get_all_buildings().items()}
    return {**resource_items, **building_items}
