import math
import uuid
from collections import defaultdict

from django.conf import settings
from django.contrib.contenttypes.fields import GenericForeignKey
from django.contrib.contenttypes.models import ContentType
from django.contrib.humanize.templatetags.humanize import intcomma
from django.db import models, transaction
from django.db.models import Q
from django.utils.functional import cached_property

from applications.enums import REGIONS, SUBREGIONS
from applications.items.models import (
    RECIPE_TYPES,
    SPECIAL_STATS,
    Building,
    Bundle,
    BundleItem,
    Item,
    NationRecipe,
    Recipe,
    Resource,
)
from applications.notifications.models import REPORT_TYPES, NationReport
from applications.items.templatetags.numbers_display import absolute_number, delta_number, number
from misc.cached import (
    get_all_buildings,
    get_all_items,
    get_all_recipes,
    get_all_resources,
)
from misc.errors import InvalidInput

from .managers import NationBuildingManager, NationResourceManager

CONSTANTS = settings.GAME_CONSTANTS


def upload_to(instance, filename):
    salt = uuid.uuid4()
    return f"flags/{salt}_{filename}".replace("-", "_")


class Nation(models.Model):
    owner = models.ForeignKey('users.User', on_delete=models.CASCADE, related_name='nations')

    name = models.CharField(max_length=50, blank=False, unique=True)
    description = models.TextField(max_length=1000, blank=True)
    flag = models.ImageField(upload_to=upload_to, blank=True, null=True)

    created_on = models.DateTimeField(auto_now_add=True)
    age = models.PositiveIntegerField(default=0)

    funds = models.BigIntegerField(default=500000)
    gdp_last_turn = models.PositiveBigIntegerField(default=0)
    satisfaction = models.IntegerField(default=0)

    se_relation = models.IntegerField(default=0)
    nlr_relation = models.IntegerField(default=0)

    region = models.PositiveSmallIntegerField(choices=REGIONS.choices)
    subregion = models.PositiveSmallIntegerField(choices=SUBREGIONS.choices)

    def __str__(self):
        return f'{self.name}'

    def save(
            self, force_insert=False, force_update=False, using=None, update_fields=None
    ):
        old = Nation.objects.filter(pk=self.pk).first()

        super().save(
            force_insert=force_insert,
            force_update=force_update,
            using=using,
            update_fields=update_fields,
        )

        if old and old.owner_id != self.owner_id:
            nation = Nation.objects.filter(owner_id=old.owner_id).exclude(pk=old.pk).first()
            old.owner.profile.active_nation = nation
            old.owner.profile.save()

        if not self.owner.profile.active_nation:
            self.owner.profile.active_nation = self
            self.owner.profile.save()

    def delete(self, using=None, keep_parents=False):
        if self.owner.profile.active_nation == self:
            nation = Nation.objects.filter(owner=self.owner).exclude(pk=self.pk).first()
            self.owner.profile.active_nation = nation
            self.owner.profile.save()

        super().delete(using=using, keep_parents=keep_parents)

    @property
    def full_region(self):
        return f'{self.get_subregion_display()} {self.get_region_display()}'

    @property
    def inflation(self):
        if self.funds > CONSTANTS['INFLATION_MIN']:
            return math.ceil((self.funds - CONSTANTS['INFLATION_MIN']) / CONSTANTS['INFLATION_DIVIDER'])
        return 0

    @property
    def resources(self):
        return NationResource.objects.filter(nation=self)

    @property
    def buildings(self):
        return NationBuilding.objects.filter(nation=self)

    @cached_property
    def per_tick(self):
        per_tick = {
            'funds': 0,
            'satisfaction': 0,
            'se_relation': 0,
            'nlr_relation': 0,
        }

        for building in self.buildings_dict.values():
            if produces := building.produces_total:
                for key in SPECIAL_STATS.keys():
                    per_tick[key] += produces[key]['amount']

            if consumes := building.consumes_total:
                for key in SPECIAL_STATS.keys():
                    per_tick[key] -= consumes[key]['amount']

        return per_tick

    @cached_property
    def resources_dict(self):
        # Same deal as buildings_dict
        resource_type = ContentType.objects.get_for_model(Resource)

        resources = dict()
        for resource in self.resources:
            resource.update_from_cache()
            resources[resource.item_id] = resource

        def calculate(building_obj, consumption=False):
            building_attribute = 'consumes_total' if consumption else 'produces_total'
            resource_attribute = 'consumed' if consumption else 'produced'

            if bundle := getattr(building_obj, building_attribute):
                for resource_id, bundle_resource_dict in bundle.items():
                    if resource_id in SPECIAL_STATS:
                        continue
                    if resource_id not in resources:
                        resources[resource_id] = NationResource.from_cache(
                            nation=self,
                            item_id=resource_id,
                            item_type=resource_type,
                            amount=0
                        )
                    from_building = bundle_resource_dict['amount']
                    current = getattr(resources[resource_id], resource_attribute)
                    setattr(resources[resource_id], resource_attribute, current + from_building)

        for building in self.buildings_dict.values():
            calculate(building, consumption=True)
            calculate(building, consumption=False)

        return resources

    @cached_property
    def resources_list(self):
        resources = list(self.resources_dict.values())
        resources.sort(key=lambda x: x.name)
        return resources

    @cached_property
    def buildings_dict(self):
        # Here we grab all building and resource data from cache and update nation buildings
        # from DB with it. This is done to avoid multiple queries to DB.

        buildings = dict()
        for building in self.buildings:
            building.update_from_cache()
            buildings[building.item_id] = building

        return buildings

    @cached_property
    def recipes_dict(self):
        nation_recipes = NationRecipe.no_prefetch.filter(
            (Q(region=self.region) | Q(region=0)) & (Q(subregion=self.subregion) | Q(subregion=0))
        )

        recipes = dict()
        for recipe in nation_recipes:
            recipe.update_from_cache(recipe_amount=1)
            recipes[recipe.pk] = recipe

        return recipes

    @cached_property
    def recipes_by_type(self):
        recipes = defaultdict(list)
        for recipe in self.recipes_dict.values():
            recipes[recipe.recipe_type].append(recipe)

        recipes_list = [{'type': key, 'name': RECIPE_TYPES(key).label, 'recipes': sorted(value, key=lambda x: x.pk)} for key, value in recipes.items()]
        recipes_list.sort(key=lambda x: x['type'])
        return recipes_list

    def buy_recipe(self, nation_recipe: NationRecipe):
        nation_items = self.items.all()
        items_dict = {(item.item_id, item.item_type_id): item for item in nation_items}
        changed_items_dict = dict()

        error_messages = []
        success_messages = []

        def add_success_message(name, amount):
            if amount == 0:
                return

            if amount > 0:
                verb = 'gained'
            else:
                verb = 'spent' if name != SPECIAL_STATS['satisfaction']['name'] else 'lost'

            success_messages.append(
                f'{verb.title()} {number(abs(amount))} {name}.'
            )

        if consumes := nation_recipe.consumes_total:
            for item_id, item_dict in consumes.items():
                if item_id in SPECIAL_STATS:
                    if item_id == 'funds' and item_dict['amount'] > self.funds:
                        error_messages.append(
                            f'Not enough bits. '
                            f'You have {number(self.funds)} out of {number(consumes["funds"]["amount"])}.'
                        )

                    setattr(self, item_id, getattr(self, item_id) - item_dict['amount'])
                    add_success_message(item_dict['name'], -item_dict['amount'])
                    continue

                current_amount = items_dict[item_id].amount if item_id in items_dict else 0
                if current_amount < item_dict['amount']:
                    error_messages.append(
                        f'Not enough {item_dict["name"]}. '
                        f'You have {number(current_amount)} out of {number(item_dict["amount"])}.'
                    )
                else:
                    items_dict[item_id].amount = current_amount - item_dict['amount']
                    changed_items_dict[item_id] = items_dict[item_id]
                    add_success_message(item_dict['name'], -item_dict['amount'])

        if error_messages:
            error_messages.insert(0, f'Failed to {nation_recipe.name} x{nation_recipe.amount}.')
            raise InvalidInput('\n'.join(error_messages))

        if produces := nation_recipe.produces_total:
            for item_id, item_dict in produces.items():
                if item_id in SPECIAL_STATS:
                    setattr(self, item_id, getattr(self, item_id) + item_dict['amount'])
                    add_success_message(item_dict['name'], item_dict['amount'])
                    continue

                if item_id in items_dict:
                    current_amount = items_dict[item_id].amount
                    items_dict[item_id].amount = current_amount + item_dict['amount']
                else:
                    items_dict[item_id] = NationItem(
                        nation=self,
                        item_id=item_id[0],
                        item_type_id=item_id[1],
                        amount=item_dict['amount']
                    )
                changed_items_dict[item_id] = items_dict[item_id]
                add_success_message(item_dict['name'], item_dict['amount'])

        report = NationReport(
            nation=self,
            text=f'Successfully executed action {nation_recipe.name} x{number(nation_recipe.amount)}.',
            details='\n'.join(success_messages),
            report_type=REPORT_TYPES.RECIPE,
        )

        with transaction.atomic():
            report.save()
            self.save()
            for item in changed_items_dict.values():
                item.save()

    def add_item(self, item_id, item_type_id, amount):
        item = self.items.filter(item_id=item_id, item_type_id=item_type_id).first()
        if item:
            item.amount += amount
        else:
            item = NationItem(
                nation=self,
                item_id=item_id,
                item_type_id=item_type_id,
                amount=amount
            )
        item.save()

    def tick(self):
        report_messages = []

        inflation = self.inflation
        if inflation:
            self.funds -= inflation
            report_messages.append(f'Your ministry of finances burned {number(inflation)} bits to battle inflation.')

        # todo government type effects

        satisfaction_multiplier = 1

        # Over-satisfaction loss
        oversatisfaction_loss = 0
        oversatisfaction_description = None

        satisfaction_thresholds = {
            250: 'A satisfied population',
            500: 'A very satisfied population',
            750: 'A loving population',
        }

        for threshold, description in satisfaction_thresholds.items():
            if self.satisfaction > threshold * satisfaction_multiplier:
                loss = (self.satisfaction - threshold * satisfaction_multiplier) / (50 * satisfaction_multiplier)
                oversatisfaction_loss += math.floor(loss)
                oversatisfaction_description = description
            else:
                break

        if oversatisfaction_loss:
            self.satisfaction -= oversatisfaction_loss
            report_messages.append(
                f'{oversatisfaction_description} is hard to keep; you lose {number(oversatisfaction_loss)} satisfaction.'
            )

        # Loss of satisfaction for having an empire of more than 1 nation
        empire_nations_count = self.owner.nations.count()
        if empire_nations_count > 1:
            empire_satisfaction_loss = math.pow(empire_nations_count - 1, 2) * 20
            # if self.government in ('Oppression', 'Alicorn Elite', 'Transponyism'): # todo government type effects
            #     empire_satisfaction_loss = empire_satisfaction_loss / 3

            empire_satisfaction_loss = math.ceil(empire_satisfaction_loss)
            self.satisfaction -= empire_satisfaction_loss
            report_messages.append(
                f'You lose {number(empire_satisfaction_loss)} satisfaction for having an empire of {number(empire_nations_count)} nations.'
            )

        def get_relationship_delta(value, thresholds):
            delta = 0
            loss_description = None
            for threshold, description in thresholds.items():
                if value > threshold:
                    delta += (value - threshold) / 50
                    loss_description = description
                else:
                    break
            return math.floor(delta), loss_description

        # Loss of relationship with the superpowers when relations are too high

        friendship_thresholds = {
            250: 'A good friend',
            400: 'A very good friend',
            800: 'An extremely good friend',
        }

        se_friendship_loss, se_friendship_description = get_relationship_delta(self.se_relation, friendship_thresholds)
        if se_friendship_loss:
            self.se_relation -= se_friendship_loss
            report_messages.append(
                f'{se_friendship_description} is hard to keep; you lose {number(se_friendship_loss)} relationship with the Solar Empire.'
            )

        nlr_friendship_loss, nlr_friendship_description = get_relationship_delta(self.nlr_relation, friendship_thresholds)
        if nlr_friendship_loss:
            self.nlr_relation -= nlr_friendship_loss
            report_messages.append(
                f'{nlr_friendship_description} is hard to keep; you lose {number(nlr_friendship_loss)} relationship with the New Lunar Republic.'
            )

        # Gain of relationship with the superpowers when relations are too low

        enmity_thresholds = {
            450: 'A bad enemy',
            700: 'A very bad enemy',
            900: 'An extremely bad enemy',
        }

        # todo check if the player is Ascending
        se_enmity_loss, se_enmity_description = get_relationship_delta(-self.se_relation, enmity_thresholds)
        if se_enmity_loss:
            self.se_relation += se_enmity_loss
            report_messages.append(
                f'{se_enmity_description} forgets eventually; you gain {number(se_enmity_loss)} relationship with the Solar Empire.'
            )

        nlr_enmity_loss, nlr_enmity_description = get_relationship_delta(-self.nlr_relation, enmity_thresholds)
        if nlr_enmity_loss:
            self.nlr_relation += nlr_enmity_loss
            report_messages.append(
                f'{nlr_enmity_description} forgets eventually; you gain {number(nlr_enmity_loss)} relationship with the New Lunar Republic.'
            )

        # Loss of relationship with the superpowers due to jealousy

        JEALOUSY_DIVIDOR = 50
        if self.nlr_relation > 0:
            se_jealousy = math.floor(self.nlr_relation / JEALOUSY_DIVIDOR)
            if se_jealousy:
                self.se_relation -= se_jealousy
                report_messages.append(
                    f'The Solar Empire does not like your good relations with the New Lunar Republic. You lose {number(se_jealousy)} relationship.'
                )

        if self.se_relation > 0:
            nlr_jealousy = math.floor(self.se_relation / JEALOUSY_DIVIDOR)
            if nlr_jealousy:
                self.nlr_relation -= nlr_jealousy
                report_messages.append(
                    f'The New Lunar Republic does not like your good relations with the Solar Empire. You lose {number(nlr_jealousy)} relationship.'
                )

        # Buildings and resources calculations
        resource_type = ContentType.objects.get_for_model(Resource)
        resources = dict()
        for resource in self.resources:
            resource.update_from_cache()
            resources[resource.item_id] = resource

        buildings = dict()
        for building in self.buildings:
            building.update_from_cache(include_satisfaction_loss=False)
            buildings[building.item_id] = building

        for building_id, building in buildings.items():
            report_messages.append(f'<strong>{number(building.total)} {building.name}:</strong>')
            building_messages = list()

            def add_success_message(resource_name, amount):
                if amount == 0:
                    return

                if amount > 0:
                    verb = 'produced'
                else:
                    special_names = (
                        SPECIAL_STATS['satisfaction']['name'],
                        SPECIAL_STATS['se_relation']['name'],
                        SPECIAL_STATS['nlr_relation']['name'],
                    )
                    verb = 'consumed' if resource_name not in special_names else 'caused loss of'

                building_messages.append(
                    f'{verb.capitalize()} {number(abs(amount))} {resource_name}.'
                )

            if building.disabled:
                disabled_loss = building.disabled
                self.satisfaction -= disabled_loss
                building_messages.append(
                    f'You lose {number(disabled_loss)} satisfaction for having {number(building.disabled)} disabled buildings.'
                )
            can_afford = True

            if consumes := building.consumes_total:
                for resource_id, resource_dict in consumes.items():
                    if resource_id in SPECIAL_STATS:
                        if resource_id == 'funds' and resource_dict['amount'] > self.funds:
                            can_afford = False
                            building_messages.append(
                                f'Not enough bits to run. '
                                f'You have {number(self.funds)} out of {number(consumes["funds"]["amount"])}.'
                            )
                    else:
                        resource = resources.get(resource_id)
                        current = resource.amount if resource else 0
                        if current < resource_dict['amount']:
                            can_afford = False
                            building_messages.append(
                                f'Not enough {resource_dict["name"]} to run. '
                                f'You have {number(current)} out of {number(resource_dict["amount"])}.'
                            )

                if can_afford:
                    for resource_id, resource_dict in consumes.items():
                        add_success_message(resource_dict['name'], -resource_dict['amount'])
                        if resource_id in SPECIAL_STATS:
                            setattr(self, resource_id, getattr(self, resource_id) - resource_dict['amount'])
                        else:
                            resources[resource_id].amount -= resource_dict['amount']
                else:
                    shutdown_loss = building.total
                    self.satisfaction -= shutdown_loss
                    building_messages.append(
                        f'You lose {number(shutdown_loss)} satisfaction for having {number(building.total)} buildings shut down.'
                    )

            if can_afford and (produces := building.produces_total):
                for resource_id, resource_dict in produces.items():
                    add_success_message(resource_dict['name'], resource_dict['amount'])
                    if resource_id in SPECIAL_STATS:
                        setattr(self, resource_id, getattr(self, resource_id) + resource_dict['amount'])
                    else:
                        if resource_id in resources:
                            resources[resource_id].amount += resource_dict['amount']
                        else:
                            resources[resource_id] = NationItem(
                                nation=self,
                                item_id=resource_id,
                                item_type=resource_type,
                                amount=resource_dict['amount'],
                            )

            if building_messages:
                elements = [f'<li>{message}</li>' for message in building_messages]
                report_messages.append(f'<ul>{"".join(elements)}</ul>')

        for resource in resources.values():
            loss = resource.loss
            if loss:
                resource.amount -= loss
                # todo add message about dumping oil in the ocean
                report_messages.append(
                    f'As you have more than {number(CONSTANTS["RESOURCE_LOSS_MIN"])} {resource.name}, {number(loss)} was siphoned off.'
                )

        # Relationship caps
        RELATIONSHIP_CAP_MAX = 1000
        RELATIONSHIP_CAP_MIN = -1000

        if self.se_relation > RELATIONSHIP_CAP_MAX:
            self.se_relation = RELATIONSHIP_CAP_MAX
            report_messages.append(
                f'The Solar Empire is not interested in your friendship anymore. Relationship capped at {number(RELATIONSHIP_CAP_MAX)}.'
            )

        if self.nlr_relation > RELATIONSHIP_CAP_MAX:
            self.nlr_relation = RELATIONSHIP_CAP_MAX
            report_messages.append(
                f'The New Lunar Republic is not interested in your friendship anymore. Relationship capped at {number(RELATIONSHIP_CAP_MAX)}.'
            )

        if self.se_relation < RELATIONSHIP_CAP_MIN:
            self.se_relation = RELATIONSHIP_CAP_MIN
            report_messages.append(
                f'Even for the Solar Empire, there are limits to hate. Relationship capped at {number(RELATIONSHIP_CAP_MIN)}.'
            )

        if self.nlr_relation < RELATIONSHIP_CAP_MIN:
            self.nlr_relation = RELATIONSHIP_CAP_MIN
            report_messages.append(
                f'Even for the New Lunar Republic, there are limits to hate. Relationship capped at {number(RELATIONSHIP_CAP_MIN)}.'
            )

        # todo tick summary
        report = NationReport(
            nation=self,
            text='tick',
            details='\n'.join(report_messages),
            report_type=REPORT_TYPES.TICK,
        )

        with transaction.atomic():
            report.save()
            for resource in resources.values():
                resource.save()
            self.save()


class NationItem(models.Model):
    nation = models.ForeignKey('Nation', on_delete=models.CASCADE, related_name='items')

    item_id = models.PositiveIntegerField()
    item_type = models.ForeignKey(
        ContentType,
        on_delete=models.CASCADE,
        limit_choices_to={'model__in': ('resource', 'building',)}
    )
    item = GenericForeignKey('item_type', 'item_id')

    amount = models.PositiveIntegerField(default=0)
    disabled = models.PositiveIntegerField(default=0)

    class Meta:
        unique_together = ('nation', 'item_type', 'item_id')

    _cached_item: dict = None

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self._cached_item = dict()

    def __str__(self):
        return f'{intcomma(self.amount)} {self.name}'

    def save(
        self, force_insert=False, force_update=False, using=None, update_fields=None
    ):
        if self.amount == 0:
            self.delete()
        else:
            super().save(force_insert, force_update, using, update_fields)

    @classmethod
    def from_cache(cls, nation, item_id, item_type, amount: int = 0):
        nation_item = cls()
        nation_item.nation = nation
        nation_item.item_id = item_id
        nation_item.item_type = item_type
        nation_item.amount = amount

        nation_item.update_from_cache()

        return nation_item

    def update_from_cache(self):
        self._cached_item = get_all_items()[(self.item_id, self.item_type_id)]

    @property
    def name(self):
        return self._cached_item.get('name') or self.item.name

    @property
    def description(self):
        return self._cached_item.get('description') or self.item.description

    @property
    def icon(self):
        if 'icon' in self._cached_item:
            return self._cached_item.get('icon')
        return self.item.icon.url if self.item.icon else None


class NationResource(NationItem):
    objects = NationResourceManager()

    class Meta:
        proxy = True

    # Attributes for nation calculations
    produced = 0
    consumed = 0

    @property
    def loss(self):
        if self.amount > CONSTANTS['RESOURCE_LOSS_MIN']:
            return math.ceil((self.amount - CONSTANTS['RESOURCE_LOSS_MIN']) / CONSTANTS['RESOURCE_LOSS_DIVIDER'])
        return 0

    @property
    def net(self):
        return self.produced - self.consumed - self.loss

    @property
    def ticks_worth(self):
        # todo revise
        if self.net == 0:
            return 0
        elif self.net > 0:
            return float('inf')

        return self.amount / self.net


class NationBuilding(NationItem):
    objects = NationBuildingManager()

    class Meta:
        proxy = True

    consumes_total = None
    produces_total = None

    # is_active = True

    def update_from_cache(self, include_satisfaction_loss: bool = False):
        super().update_from_cache()

        # I use total = float(0) when I need to indicate that this building
        # produces this item in general, but not now because it's disabled
        total = self.total
        if total == 0:
            total = 0.0

        building = self._cached_item
        resources = get_all_resources()

        # todo refactor to merge consumes and produces logic
        if consumes := building.get('consumes'):
            self.consumes_total = dict()
            for key in SPECIAL_STATS.keys():
                stat = SPECIAL_STATS[key].copy()
                stat['amount'] = consumes[key] * total if consumes[key] else 0
                self.consumes_total[key] = stat
            for (resource_id, _), amount in consumes['items'].items():
                resource = resources[resource_id].copy()
                resource['amount'] = amount * total if amount else 0
                self.consumes_total[resource_id] = resource

        if produces := building.get('produces'):
            self.produces_total = dict()
            for key in SPECIAL_STATS.keys():
                stat = SPECIAL_STATS[key].copy()
                stat['amount'] = produces[key] * total if produces[key] else 0
                self.produces_total[key] = stat
            for (resource_id, _), amount in produces['items'].items():
                resource = resources[resource_id].copy()
                resource['amount'] = amount * total if amount else 0
                self.produces_total[resource_id] = resource

            if include_satisfaction_loss:
                # Softcap penalty
                self.produces_total['satisfaction']['amount'] -= self.softcap_penalty
                # Disabled penalty
                self.produces_total['satisfaction']['amount'] -= self.disabled

            # Round satisfaction to int
            # if self.produces_total['satisfaction']['amount'] != 0:
            #     self.produces_total['satisfaction']['amount'] = int(self.produces_total['satisfaction']['amount'])

    @property
    def total(self):
        return self.amount - self.disabled

    @property
    def consumes(self):
        return self._cached_item.get('consumes') if 'consumes' in self._cached_item else self.item.consumes

    @property
    def produces(self):
        return self._cached_item.get('produces') if 'produces' in self._cached_item else self.item.produces

    @property
    def softcap(self):
        return self._cached_item.get('softcap') if 'softcap' in self._cached_item else self.item.softcap

    @property
    def softcap_divider(self):
        return self._cached_item.get('softcap_divider') or self.item.softcap_divider

    @property
    def softcap_penalty(self):
        # noinspection PyChainedComparisons
        if self.softcap > 0 and self.total > self.softcap:
            return math.ceil((self.total - self.softcap) ** 2 / self.softcap_divider)
        return 0

    @property
    def satisfaction_on_destroy(self):
        return self._cached_item.get('satisfaction_on_destroy') or self.item.satisfaction_on_destroy

    def enable(self, amount: int, save=True):
        if amount < 0:
            raise InvalidInput('Amount of buildings to enable can`t be less than 0')
        if amount > self.disabled:
            raise InvalidInput('Amount of buildings to enable can`t greater than amount of disabled buildings')

        self.disabled -= amount

        if save:
            self.save()

    def disable(self, amount: int, save=True):
        if amount < 0:
            raise InvalidInput('Amount of buildings to disable can`t be less than 0')
        if amount > self.total:
            raise InvalidInput('Amount of buildings to disable can`t greater than amount of enabled buildings')

        self.disabled += amount

        if save:
            self.save()

    def destroy(self, amount: int, save=True):
        if amount < 0:
            raise InvalidInput('Amount of buildings to destroy can`t be less than 0')
        if amount > self.amount:
            raise InvalidInput('Amount of buildings to destroy can`t be greater than total amount of buildings')

        satisfaction = self.satisfaction_on_destroy * amount

        self.amount -= amount
        self.nation.satisfaction += satisfaction

        if save:
            with transaction.atomic():
                self.nation.save()
                self.save()

        return satisfaction
