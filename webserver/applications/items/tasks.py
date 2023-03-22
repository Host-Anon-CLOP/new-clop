from django.core.cache import cache

from misc.cached import (
    get_all_buildings,
    get_all_items,
    get_all_recipes,
    get_all_resources,
)

from .models import Building, Recipe, Resource


def update_cache():
    """Update the cache of all items."""
    resources = {resource.id: resource.as_dict for resource in Resource.objects.all()}
    buildings = {building.id: building.as_dict for building in Building.objects.all()}
    recipes = {recipe.id: recipe.as_dict for recipe in Recipe.objects.all()}

    to_cache = dict(
        resources=resources,
        buildings=buildings,
        recipes=recipes,
    )
    cache.set_many(to_cache, timeout=None)

    get_all_items.cache_clear()
    get_all_recipes.cache_clear()
    get_all_buildings.cache_clear()
    get_all_resources.cache_clear()

    print('Cache updated')
