from django.contrib import admin

from .models import Order

# todo cancel order action


@admin.register(Order)
class OrderAdmin(admin.ModelAdmin):
    search_fields = ('nation__name',)
    list_filter = ('order_type',)
    list_display = ('nation', 'item_name', 'price', 'amount', 'order_type', 'created_at',)

    @admin.display(description='Item')
    def item_name(self, obj):
        return obj.item.name

