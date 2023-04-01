from django.core.cache import cache

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

    print('Cache updated')
