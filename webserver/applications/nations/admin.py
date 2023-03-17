from django.contrib import admin
from django.utils.translation import gettext_lazy as _

from .models import Nation, NationItem


class NationItemInline(admin.TabularInline):
    model = NationItem
    extra = 1


@admin.register(Nation)
class NationAdmin(admin.ModelAdmin):
    inlines = (NationItemInline, )

    fieldsets = (
        (None, {'fields': ('owner', 'name', 'description', 'flag', 'region', 'subregion')}),
        ('Dates', {'fields': ('age', )}),
        ('Numbers', {'fields': ('funds', 'gdp_last_turn', 'satisfaction', 'se_relation', 'nlr_relation',)})
    )

    list_display = ('owner', 'name', 'age')
    search_fields = ('owner__username', 'name',)

    # def owner_stasis(self, nation):
    #     return nation.owner.profile.stasis
