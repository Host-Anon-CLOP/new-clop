import functools

from django.contrib.contenttypes.models import ContentType
from django.core.cache import cache, caches


local_cache = caches['local']


def cache_func_local(func):
    @functools.wraps(func)
    def wrapper(*args, **kwargs):
        key = f'{func.__name__}{args}{kwargs}'
        result = local_cache.get(key)
        if result is None:
            result = func(*args, **kwargs)
            local_cache.set(key, result)
        return result
    return wrapper


@cache_func_local
def get_all_buildings():
    return cache.get('buildings')


@cache_func_local
def get_all_resources():
    return cache.get('resources')


@cache_func_local
def get_all_recipes():
    return cache.get('recipes')


@cache_func_local
def get_all_items():
    from applications.items.models import Building, Resource

    resource_type = ContentType.objects.get_for_model(Resource).pk
    building_type = ContentType.objects.get_for_model(Building).pk

    resource_items = {(item_id, resource_type): item for item_id, item in get_all_resources().items()}
    building_items = {(item_id, building_type): item for item_id, item in get_all_buildings().items()}
    return {**resource_items, **building_items}
