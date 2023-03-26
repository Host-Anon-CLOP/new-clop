from django.contrib.contenttypes.models import ContentType
from django.shortcuts import render, redirect
from django.views.generic import TemplateView, View
from django.contrib import messages
from applications.items.templatetags.numbers_display import absolute_number, delta_number, number

from misc.errors import exception_to_message, InvalidInput
from misc.views import HasNationMixin


from applications.items.models import Resource

from .models import Order, OrderTypes, order_type_str


class MarketView(HasNationMixin, TemplateView):
    template_name = 'markets/market.html'

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)

        resources = Resource.objects.filter(tradable=True)
        context['tradables'] = [
            ('resources', ContentType.objects.get_for_model(Resource).id, resources),
            ('weapons', 0, []),
            ('armors', 0, []),
            # ('favorites', 0, []),
        ]

        item_param = self.request.GET.get('item', None)
        if item_param:
            item_type, item_id = map(int, item_param.split('-'))
            context['selected_item'] = (item_type, item_id)

            item_type = ContentType.objects.get(pk=item_type)
            item = item_type.get_object_for_this_type(pk=item_id)
            context['item'] = item

            sell_orders = Order.objects.filter(item_id=item_id, item_type=item_type, order_type=OrderTypes.SELL).select_related('nation').order_by('price', '-created_at')
            buy_orders = Order.objects.filter(item_id=item_id, item_type=item_type, order_type=OrderTypes.BUY).select_related('nation').order_by('-price', '-created_at')
            context['sell_orders'] = sell_orders
            context['buy_orders'] = buy_orders

        return context


class CreateOrderView(HasNationMixin, View):
    def post(self, request, *args, **kwargs):
        item_type_id = int(request.POST['item_type_id'])
        item_id = int(request.POST['item_id'])

        item_type = ContentType.objects.get(pk=item_type_id)
        item = item_type.get_object_for_this_type(pk=item_id)

        amount = int(request.POST['amount'])
        price = int(request.POST['price'])
        # order_type = OrderTypes.BUY if 'buy' in request.POST else OrderTypes.SELL

        with exception_to_message(request):
            if 'buy' in request.POST:
                order_type = OrderTypes.BUY
            elif 'sell' in request.POST:
                order_type = OrderTypes.SELL
            else:
                raise InvalidInput('Invalid order type')

            order = Order.create(item, amount, price, order_type, request.user.nation)

        messages.success(request,
                         f'Successfully created a {order_type_str[order_type]} for {number(amount)} {item.name} '
                         f'at {number(price)} bits each ({number(order.total_price)} bits total)'
                         )

        response = redirect('market')
        response['Location'] += f'?item={item_type_id}-{item_id}'
        return response


class CancelOrderView(HasNationMixin, View):
    def post(self, request, *args, **kwargs):
        order_id = kwargs['order_id']

        with exception_to_message(request):
            try:
                order = Order.objects.get(pk=order_id)
            except Order.DoesNotExist:
                raise InvalidInput('Order does not exist')

            if order.nation_id != request.user.nation.id:
                raise InvalidInput('Nation does not own this order')

            order.cancel()

        messages.success(request,
                         f'Successfully cancelled {order_type_str[order.order_type]} for {number(order.amount)} {order.item.name} '
                         f'at {number(order.price)} bits each ({number(order.total_price)} bits total)')

        response = redirect('market')
        response['Location'] += f'?item={order.item_type_id}-{order.item_id}'
        return response


class FulfillOrderView(HasNationMixin, View):
    def post(self, request, *args, **kwargs):
        order_id = kwargs['order_id']
        amount = int(request.POST['amount'])
        nation = request.user.nation

        with exception_to_message(request):
            try:
                order = Order.objects.get(pk=order_id)
            except Order.DoesNotExist:
                raise InvalidInput('Order does not exist anymore')

            if order.nation_id == request.user.nation.id:
                raise InvalidInput('Nation cannot fulfill its own order')

            if 'fulfill' in request.POST:
                order.fulfill(amount, nation)
            elif 'fulfill_all' in request.POST:
                order.fulfill(order.amount, nation)
            else:
                raise InvalidInput('Invalid action')

        # messages.success(request,
        #                  f'Successfully fulfilled {order_type_str[order.order_type]} for {number(order.amount)} {order.item.name} '
        #                  f'at {number(order.price)} bits each ({number(order.total_price)} bits total)')

        response = redirect('market')
        response['Location'] += f'?item={order.item_type_id}-{order.item_id}'
        return response
