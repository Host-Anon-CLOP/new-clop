from django.contrib.contenttypes.fields import GenericForeignKey
from django.contrib.contenttypes.models import ContentType
from django.db import models, transaction

from applications.notifications.models import NationReport, REPORT_TYPES
from applications.nations.models import NationItem
from misc.errors import InvalidInput
from applications.items.templatetags.numbers_display import absolute_number, delta_number, number


class OrderTypes(models.IntegerChoices):
    BUY = 1, 'Buy'  # Nation deposits funds, receives items
    SELL = 2, 'Sell'  # Nation deposits items, receives funds


order_type_str = {
    OrderTypes.BUY: 'buy order',
    OrderTypes.SELL: 'sell offer',
}


class Order(models.Model):
    """Model definition for Order."""
    item_id = models.PositiveIntegerField()
    item_type = models.ForeignKey(
        ContentType,
        on_delete=models.CASCADE,
        limit_choices_to={'model__in': ('resource',)}
    )
    item = GenericForeignKey('item_type', 'item_id')

    amount = models.PositiveIntegerField()
    price = models.PositiveIntegerField()
    order_type = models.PositiveSmallIntegerField(choices=OrderTypes.choices)
    created_at = models.DateTimeField(auto_now_add=True)

    nation = models.ForeignKey('nations.Nation', on_delete=models.CASCADE)

    # class Meta:
    #     ordering = ['-price', 'created_at']

    def __str__(self):
        return f'{self.get_order_type_display()} {self.amount} {self.item.name} for {self.price} (by {self.nation.name})'

    @classmethod
    def create(cls, item, amount, price, order_type, nation):
        if amount <= 0:
            raise InvalidInput(f'Amount must be greater than {number(0)}')

        if price < 1000:
            raise InvalidInput(f'Price must be greater than {number(1000)}')

        if price >= 5000000:
            raise InvalidInput(f'No fun allowed. Price must be less than {number(5000000)}')

        # todo
        # existing_order = cls.objects.filter(
        #     item_id=item.id,
        #     item_type_id=ContentType.objects.get_for_model(item).id,
        #     price=price,
        #     order_type=order_type,
        #     nation=nation,
        # ).first()
        #
        # if existing_order:
        #     existing_amount = existing_order.amount
        #     existing_order.cancel()
        #     amount += existing_amount

        order = cls(item=item, amount=amount, price=price, order_type=order_type, nation=nation)

        if order_type == OrderTypes.BUY:
            if nation.funds < order.total_price:
                raise InvalidInput(f'Not enough bits to create buy order of {number(amount)} {item.name}.\n'
                                   f'You have {number(nation.funds)} out of {number(order.total_price)} bits.')

            nation.funds -= order.total_price
            with transaction.atomic():
                order.save()
                nation.save()

        elif order_type == OrderTypes.SELL:
            # get item content type
            nation_item = nation.items.filter(item_id=item.id, item_type_id=ContentType.objects.get_for_model(item).id).first()
            if not nation_item or nation_item.amount < amount:
                raise InvalidInput(f'Not enough {item.name} to create sell offer.\n'
                                   f'You have {number(nation_item.amount)} out of {number(amount)} {item.name}.')

            nation_item.amount -= amount
            with transaction.atomic():
                order.save()
                nation_item.save()

        return order

    def cancel(self):
        if self.order_type == OrderTypes.BUY:
            self.nation.funds += self.total_price
            self.delete()

        elif self.order_type == OrderTypes.SELL:
            nation_item = self.nation.items.filter(item_id=self.item_id, item_type_id=self.item_type).first()
            if nation_item:
                nation_item.amount += self.amount
            else:
                nation_item = NationItem(nation=self.nation, item=self.item, amount=self.amount)
            with transaction.atomic():
                nation_item.save()
                self.delete()

    def give_buyer_items(self, buyer, amount):
        buyer_item = buyer.items.filter(item_id=self.item_id, item_type_id=self.item_type).first()
        if buyer_item:
            buyer_item.amount += amount
        else:
            buyer_item = NationItem(nation=buyer, item=self.item, amount=amount)
        return buyer_item

    def fulfill(self, amount, nation):
        if amount <= 0:
            raise InvalidInput(f'Amount must be greater than {number(0)}')
        if amount > self.amount:
            raise InvalidInput(f'Amount is greater than order amount ({number(self.amount)}')

        self.amount -= amount

        if self.order_type == OrderTypes.BUY:
            # seller (initiator/fulfiller) gives items, receives funds
            # buyer (order creator) receives items, funds are already taken

            seller = nation
            buyer = self.nation

            seller_item = seller.items.filter(item_id=self.item_id, item_type_id=self.item_type).first()
            seller_item_amount = seller_item.amount if seller_item else 0
            if seller_item_amount < amount:
                raise InvalidInput(f'Not enough {self.item.name} to fulfill buy order.\n'
                                   f'You have {number(seller_item_amount)} out of {number(amount)} {self.item.name}.')
            seller_item.amount -= amount

            taxed_price = amount * self.price  # todo tax here
            seller.funds += taxed_price

            buyer_item = self.give_buyer_items(buyer, amount)

            buyer_report = NationReport(
                nation=buyer,
                report_type=REPORT_TYPES.MARKET,
                text=f'{seller.name} fulfilled your buy order for {number(amount)} {self.item.name} for {number(self.price)} bits each.',
                details=f'Item: {self.item.name}\n'
                        f'Amount: {number(amount)}\n'
                        f'Price: {number(self.price)} bits per unit\n'
                        f'Seller: {seller.name}'
            )

            seller_report = NationReport(
                nation=seller,
                report_type=REPORT_TYPES.MARKET,
                text=f'You sold {number(amount)} {self.item.name} to {buyer.name} for {number(taxed_price)} bits ({number(self.price)} bits each).',
                details=f'Item: {self.item.name}\n'
                        f'Amount: {number(amount)}\n'
                        f'Price: {number(self.price)} bits per unit\n'
                        f'Buyer: {buyer.name}'
            )

            with transaction.atomic():
                seller.save()
                seller_item.save()
                buyer_item.save()
                buyer_report.save()
                seller_report.save()
                self.save()

        else:
            # seller (order creator) receives funds, items are already taken
            # buyer (initiator/fulfiller) gives funds, receives items

            seller = self.nation
            buyer = nation

            taxed_price = amount * self.price  # todo tax here

            if buyer.funds < amount * self.price:
                raise InvalidInput(f'Not enough bits to buy {number(amount)} {self.item.name}.\n'
                                   f'You have {number(buyer.funds)} out of {number(taxed_price)} bits.')

            buyer.funds -= taxed_price

            buyer_item = self.give_buyer_items(buyer, amount)

            seller.funds += amount * self.price

            buyer_report = NationReport(
                nation=buyer,
                report_type=REPORT_TYPES.MARKET,
                text=f'You bought {number(amount)} {self.item.name} from {seller.name} for {number(taxed_price)} bits ({number(self.price)} each).',
                details=f'Item: {self.item.name}\n'
                        f'Amount: {number(amount)}\n'
                        f'Price: {number(self.price)} bits per unit\n'
                        f'Seller: {seller.name}'
            )

            seller_report = NationReport(
                nation=seller,
                report_type=REPORT_TYPES.MARKET,
                text=f'{buyer.name} bought your {number(amount)} {self.item.name} for {number(amount * self.price)} bits ({number(self.price)} bits each).',
                details=f'Item: {self.item.name}\n'
                        f'Amount: {number(amount)}\n'
                        f'Price: {number(self.price)} bits per unit\n'
                        f'Buyer: {buyer.name}'
            )

            with transaction.atomic():
                seller.save()
                buyer.save()
                buyer_item.save()
                buyer_report.save()
                seller_report.save()
                self.save()

    def save(
        self, force_insert=False, force_update=False, using=None, update_fields=None
    ):
        if self.amount <= 0:
            self.delete()
        else:
            super().save(force_insert, force_update, using, update_fields)

    @property
    def total_price(self):
        return self.amount * self.price

    @property
    def tax(self):
        return 0.1  # todo government effects

    @property
    def price_taxed(self):
        return self.price * (1 + self.tax)
