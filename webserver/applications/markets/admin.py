from django.contrib import admin

from .models import Order, Transaction

# todo cancel order action


@admin.register(Order)
class OrderAdmin(admin.ModelAdmin):
    search_fields = ('nation__name',)
    list_filter = ('order_type', 'created_on',)
    list_display = ('nation', 'item_name', 'amount', 'price', 'order_type', 'created_on',)

    @admin.display(description='Item')
    def item_name(self, obj):
        return obj.item.name


@admin.register(Transaction)
class TransactionAdmin(admin.ModelAdmin):
    search_fields = ('buyer__name', 'seller__name')
    list_filter = ('order_type', 'created_on',)
    list_display = ('buyer', 'seller', 'item_name', 'amount', 'price', 'total_price', 'order_type', 'created_on',)

    @admin.display(description='Item')
    def item_name(self, obj):
        return obj.item.name

    def has_add_permission(self, request):
        return False

    def has_change_permission(self, request, obj=None):
        return False
