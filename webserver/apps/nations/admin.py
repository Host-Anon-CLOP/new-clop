from django.contrib import admin
from django.utils.translation import gettext_lazy as _

from .models import Nation


@admin.register(Nation)
class NationAdmin(admin.ModelAdmin):
    fieldsets = (
        (None, {'fields': ('owner', 'name', 'description', 'region', 'subregion')}),
        ('Dates', {'fields': ('age', )}),
        ('Numbers', {'fields': ('funds', 'gdp_last_turn', 'satisfaction', 'se_relation', 'nlr_relation',)})
    )

    list_display = ('owner', 'name', 'age')
    search_fields = ('owner__username', 'name',)

    # def owner_stasis(self, nation):
    #     return nation.owner.profile.stasis
