from django.contrib import admin
from django.utils.translation import gettext_lazy as _

from .models import Nation, NationItem

from applications.markets.models import Order


class NationItemInline(admin.TabularInline):
    model = NationItem
    extra = 1


class OrderInline(admin.TabularInline):
    model = Order
    extra = 1
    fields = ('item_id', 'item_type', 'amount', 'price', 'order_type', 'created_on', )
    readonly_fields = ('created_on', )
    show_change_link = True


@admin.register(Nation)
class NationAdmin(admin.ModelAdmin):
    inlines = (NationItemInline, OrderInline,)

    fieldsets = (
        (None, {'fields': ('owner', 'name', 'description', 'flag', 'region', 'subregion')}),
        ('Dates', {'fields': ('age', )}),
        ('Numbers', {'fields': ('funds', 'gdp_last_turn', 'satisfaction', 'se_relation', 'nlr_relation',)})
    )

    list_display = ('owner', 'name', 'age')
    search_fields = ('owner__username', 'name',)

    # def owner_stasis(self, nation):
    #     return nation.owner.profile.stasis
