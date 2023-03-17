from django.contrib import admin

from .models import Building, Bundle, BundleItem, Item, Recipe, Resource


class ItemInline(admin.TabularInline):
    model = BundleItem
    extra = 1


@admin.register(Resource)
class ResourceAdmin(admin.ModelAdmin):
    list_display = ('id', 'name', 'tradable')
    search_fields = ('id', 'name', )
    list_filter = ('tradable', )


@admin.register(Building)
class BuildingAdmin(admin.ModelAdmin):
    list_display = ('id', 'name', 'consumes', 'produces', 'softcap')
    search_fields = ('id', 'name', )


@admin.register(Bundle)
class BundleAdmin(admin.ModelAdmin):
    inlines = (ItemInline, )


@admin.register(Recipe)
class RecipeAdmin(admin.ModelAdmin):
    list_display = ('id', 'name', 'recipe_type', 'consumes', 'produces')
    search_fields = ('id', 'name', )
    list_filter = ('recipe_type', )

