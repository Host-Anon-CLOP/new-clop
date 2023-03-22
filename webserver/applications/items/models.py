from django.contrib.contenttypes.fields import GenericForeignKey, GenericRelation
from django.contrib.contenttypes.models import ContentType
from django.contrib.humanize.templatetags.humanize import intcomma
from django.db import models

from misc.cached import (
    get_all_buildings,
    get_all_items,
    get_all_recipes,
    get_all_resources,
)

from ..enums import RECIPE_TYPES, REGIONS_ANY, SUBREGIONS_ANY
from .managers import BuildingManager, BundleItemManager, BundleManager, RecipeManager

SPECIAL_STATS = {
    'funds': {'name': 'Bits', },
    'satisfaction': {'name': 'Satisfaction', },
    'se_relation': {'name': 'SE Relation', },
    'nlr_relation': {'name': 'NLR Relation', },
}

# EXTRA_SPECIAL_STATS = SPECIAL_STATS.copy()
# ECOLOGY = {'name': 'Ecology dissatisfaction', }
# EXTRA_SPECIAL_STATS.update({'ecology': ECOLOGY})


class Item(models.Model):
    name = models.CharField(max_length=100)
    description = models.TextField()
    icon = models.ImageField(upload_to='items/icons', blank=True, null=True)

    # objects = InheritanceManager()

    def __str__(self):
        return f'{self.id}. {self.name}'

    class Meta:
        abstract = True


class Resource(Item):
    tradable = models.BooleanField(default=True)

    @property
    def as_dict(self):
        return dict(
            id=self.id,
            name=self.name,
            description=self.description,
            icon=self.icon.url if self.icon else None,
            tradable=self.tradable,
        )


class Building(Item):
    satisfaction_on_destroy = models.SmallIntegerField(default=0)

    softcap = models.PositiveSmallIntegerField(default=0)
    softcap_divider = models.PositiveSmallIntegerField(default=1)

    consumes = models.ForeignKey('Bundle', null=True, on_delete=models.SET_NULL, related_name='buildings_consumes')
    produces = models.ForeignKey('Bundle', null=True, on_delete=models.SET_NULL, related_name='buildings_produces')

    objects = BuildingManager()
    no_prefetch = models.Manager()

    @property
    def as_dict(self):
        return dict(
            id=self.id,
            name=self.name,
            description=self.description,
            icon=self.icon.url if self.icon else None,
            satisfaction_on_destroy=self.satisfaction_on_destroy,
            softcap=self.softcap,
            softcap_divider=self.softcap_divider,
            consumes=self.consumes.as_dict if self.consumes else None,
            produces=self.produces.as_dict if self.produces else None,
        )


class Bundle(models.Model):
    funds = models.IntegerField(default=0)
    satisfaction = models.SmallIntegerField(default=0)

    se_relation = models.SmallIntegerField(default=0)
    nlr_relation = models.SmallIntegerField(default=0)

    objects = BundleManager()
    no_prefetch = models.Manager()

    def __str__(self):
        fields = dict(
            funds=self.funds,
            satisfaction=self.satisfaction,
            se_relation=self.se_relation,
            nlr_relation=self.nlr_relation,
        )
        fields = {name.title(): amount for name, amount in fields.items() if amount != 0}

        items = {bundled.name: bundled.amount for bundled in self.items.all()}
        fields.update(items)
        return '; '.join([f'{intcomma(amount)} {name}' for name, amount in fields.items()])

    @property
    def items_dict(self):
        return {(bundled.item_id, bundled.item_type.id): bundled.amount for bundled in self.items.all()}

    @property
    def as_dict(self):
        return {
            'funds': self.funds,
            'satisfaction': self.satisfaction,
            'se_relation': self.se_relation,
            'nlr_relation': self.nlr_relation,
            'items': self.items_dict,
        }


class BundleItem(models.Model):
    bundle = models.ForeignKey('Bundle', on_delete=models.CASCADE, related_name='items')

    item_id = models.PositiveIntegerField()
    item_type = models.ForeignKey(ContentType, on_delete=models.CASCADE, limit_choices_to={'model__in': ('resource', 'building',)})
    item = GenericForeignKey('item_type', 'item_id')

    amount = models.SmallIntegerField(default=1)

    objects = BundleItemManager()
    no_prefetch = models.Manager()

    class Meta:
        unique_together = ('bundle', 'item_type', 'item_id')

    def __str__(self):
        return f'{intcomma(self.amount)} {self.name}'

    @property
    def name(self):
        return self.item.name

    @property
    def description(self):
        return self.item.description

    @property
    def icon(self):
        return self.item.icon.url if self.item.icon else None

    @property
    def as_dict(self):
        return dict(
            id=self.item_id,
            type=self.item_type.id,
            name=self.name,
            description=self.description,
            icon=self.icon,
            amount=self.amount,
        )


class Recipe(models.Model):
    name = models.CharField(max_length=100)
    description = models.TextField()
    recipe_type = models.PositiveSmallIntegerField(choices=RECIPE_TYPES.choices)

    region = models.PositiveSmallIntegerField(choices=REGIONS_ANY.choices)
    subregion = models.PositiveSmallIntegerField(choices=SUBREGIONS_ANY.choices)

    consumes = models.ForeignKey('Bundle', null=True, on_delete=models.SET_NULL, related_name='recipes_consumes')
    produces = models.ForeignKey('Bundle', null=True, on_delete=models.SET_NULL, related_name='recipes_produces')

    objects = RecipeManager()
    no_prefetch = models.Manager()

    def __str__(self):
        return f'{self.id}. {self.name}'

    @property
    def as_dict(self):
        return dict(
            id=self.id,
            name=self.name,
            description=self.description,
            recipe_type=self.recipe_type,
            region=self.region,
            subregion=self.subregion,
            consumes=self.consumes.as_dict if self.consumes else None,
            produces=self.produces.as_dict if self.produces else None,
        )


class NationRecipe(Recipe):
    class Meta:
        proxy = True

    consumes_total: dict = None
    produces_total: dict = None
    amount = 1

    building = None

    def update_from_cache(self, recipe_amount=1):
        if recipe_amount < 1:
            raise ValueError('Recipe amount must be at least 1.')

        self.amount = recipe_amount

        recipe = get_all_recipes()[self.pk]
        items = get_all_items()

        if consumes := recipe.get('consumes'):
            self.consumes_total = dict()
            for key in SPECIAL_STATS.keys():
                stat = SPECIAL_STATS[key].copy()
                stat['amount'] = consumes[key] * self.amount
                self.consumes_total[key] = stat
            for item_key, amount in consumes['items'].items():
                item = items[item_key].copy()
                item['amount'] = amount * self.amount
                self.consumes_total[item_key] = item

        if produces := recipe.get('produces'):
            self.produces_total = dict()
            for key in SPECIAL_STATS.keys():
                stat = SPECIAL_STATS[key].copy()
                stat['amount'] = produces[key] * self.amount
                self.produces_total[key] = stat
            for item_key, amount in produces['items'].items():
                item = items[item_key].copy()
                item['amount'] = amount * self.amount
                self.produces_total[item_key] = item

            if produces['items']:
                building_id, building_amount = next(iter(produces['items'].items()))

                building_type = ContentType.objects.get_for_model(Building)
                if building_id[1] == building_type.id:
                    from applications.nations.models import NationBuilding
                    building = NationBuilding(
                        item_id=building_id[0],
                        item_type=building_type,
                        amount=building_amount,
                    )
                    building.update_from_cache()
                    self.building = building
