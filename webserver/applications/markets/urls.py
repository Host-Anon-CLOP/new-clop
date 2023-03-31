from django.urls import path

from .views import MarketView, CreateOrderView, CancelOrderView, FulfillOrderView, MyOrdersView

urlpatterns = [
    path('', MarketView.as_view(), name='market'),
    path('create_order/', CreateOrderView.as_view(), name='create_order'),
    path('order/<int:order_id>/cancel/', CancelOrderView.as_view(), name='cancel_order'),
    path('order/<int:order_id>/fulfill/', FulfillOrderView.as_view(), name='fulfill_order'),
    path('my_orders/', MyOrdersView.as_view(), name='my_orders'),
]
