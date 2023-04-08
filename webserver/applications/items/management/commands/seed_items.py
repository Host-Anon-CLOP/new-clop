from pathlib import Path

from django.core.files import File
from django.core.management.base import BaseCommand
from django.core.management.color import no_style
from django.db import connection
from django.utils import timezone
from django_q.models import Schedule

from applications.enums import RECIPE_TYPES, REGIONS_ANY, SUBREGIONS_ANY
from applications.items.models import (
    Building,
    Bundle,
    BundleItem,
    Item,
    Recipe,
    Resource,
)

# Definition utilities


def filter_none(**kwargs):
    return {key: value for key, value in kwargs.items() if value is not None}


def resource(
        name,
        description=None,
        icon=None,
        tradable=None,
):
    defaults = filter_none(
        description=description,
        tradable=tradable,
    )
    obj, _ = Resource.objects.update_or_create(name=name, defaults=defaults)
    if icon is not None:
        obj.icon.save(icon.name, File(open(icon, 'rb')))
    return obj


def building(
        name,
        description=None,
        satisfaction_on_destroy=None,
        softcap=None,
        softcap_divider=None,
        consumes=None,
        produces=None,
        ):
    defaults = filter_none(
        description=description,
        satisfaction_on_destroy=satisfaction_on_destroy,
        softcap=softcap,
        softcap_divider=softcap_divider,
        consumes=consumes,
        produces=produces,
    )
    obj, _ = Building.no_prefetch.update_or_create(name=name, defaults=defaults)
    return obj


def bundle(
        funds=None,
        satisfaction=None,
        se_relation=None,
        nlr_relation=None,
        items=None,
):
    items = items or dict()
    defaults = filter_none(
        funds=funds,
        satisfaction=satisfaction,
        se_relation=se_relation,
        nlr_relation=nlr_relation,
    )
    bundle_obj = Bundle.no_prefetch.create(**defaults)

    for item, amount in items.items():
        bundle_obj.items.create(item=item, amount=amount)

    return bundle_obj


def recipe(
        name,
        description=None,
        recipe_type=None,
        region=REGIONS_ANY.ANY,
        subregion=SUBREGIONS_ANY.ANY,
        consumes=None,
        produces=None,
        ):
    defaults = filter_none(
        description=description,
        recipe_type=recipe_type,
        region=region,
        subregion=subregion,
        consumes=consumes,
        produces=produces,
    )
    obj, _ = Recipe.no_prefetch.update_or_create(name=name, defaults=defaults)
    return obj


class Command(BaseCommand):
    def add_arguments(self, parser):
        parser.add_argument('-c', '--clear', action='store_true', help='Clear all item models')

    def handle(self, *args, **options):
        # Cleanup
        clear = options.get('clear', False)

        BundleItem.no_prefetch.all().delete()
        Bundle.no_prefetch.all().delete()
        to_reset_ids = [Bundle, BundleItem]

        if clear:
            Resource.objects.all().delete()
            Building.no_prefetch.all().delete()
            Recipe.no_prefetch.all().delete()

            to_reset_ids.extend([Resource, Building, Recipe])

        # Reset ids sequence
        sequence_sql = connection.ops.sequence_reset_sql(no_style(), to_reset_ids)
        with connection.cursor() as cursor:
            for sql in sequence_sql:
                cursor.execute(sql)

        icons = Path(__file__).parent / 'icons'

        # Resource definitions
        oil = resource(
            name='Oil',
            icon=icons / 'Oil.png',
            description='The stuff of life and the backbone of the >CLOP economy.'
        )

        copper = resource(
            name='Copper',
            icon=icons / 'Copper.png',
            description="It's a good thing that copper is so common, because it's fundamental to the manufacture of every technological component."
        )

        apples = resource(
            name='Apples',
            icon=icons / 'Apples.png',
            description='A pony without apples is an unhappy pony. Unhappy ponies will overthrow you and trot on your corpse. Keep your ponies happy. Give them apples.'
        )

        energy = resource(
            name='Energy',
            icon=icons / 'Energy.png',
            description='Batteries, watts, juice- call it what you want, you need more of this, whether you burn oil for it or not.',
            tradable=False,
        )

        vehicle_parts = resource(
            name='Vehicle Parts',
            icon=icons / 'VehicleParts.png',
            description='These vehicle parts have many uses, first among them being to make life easier on ponies who work in farms, mines, and oil wells, turning a nasty job into a slightly less nasty one.',
        )

        machinery_parts = resource(
            name='Machinery Parts',
            icon=icons / 'MachineryParts.png',
            description='These machinery parts are used in the manufacture of advanced structures.',
        )

        pies = resource(
            name='Pies',
            icon=icons / 'Pies.png',
            description='Distributing these baked goodies brings your little ponies happiness up quickly',
        )

        recipe(
            name='Burn Oil',
            description='Burn oil in inefficient, hand-me-down generators in a wasteful process that severely pollutes the air and only yields small amount of energy.',
            recipe_type=RECIPE_TYPES.BASIC_ACTIONS,
            consumes=bundle(
                items={oil: 5}
            ),
            produces=bundle(
                satisfaction=-5,
                items={energy: 5}
            ),
        )

        recipe(
            name='Distribute Apples',
            description='Distributing apples directly to your little ponies is highly inefficient, but at least it gets the job done and keeps them happy enough.',
            recipe_type=RECIPE_TYPES.BASIC_ACTIONS,
            consumes=bundle(
                items={apples: 5},
            ),
            produces=bundle(
                satisfaction=3,
            ),
        )

        recipe(
            name='Distribute Money',
            description='This is probably the worst use of money possible and won`t work in the long run, but if you`re desperately trying to stave off losing your country... well, it`s better than nothing.',
            recipe_type=RECIPE_TYPES.BASIC_ACTIONS,
            consumes=bundle(
                funds=100000,
            ),
            produces=bundle(
                satisfaction=1,
            ),
        )

        basic_factory = building(
            name='Basic Factory',
            description='Little more than a series of primitive CNC machines and some aging control systems, this factory makes everything from basic gun parts to pieces of more advanced factories.',
            satisfaction_on_destroy=0,
            softcap=20,
            softcap_divider=10,
            consumes=bundle(
                items={energy: 1}
            ),
            produces=bundle(
                satisfaction=-1,
                funds=10000,
            ),
        )

        recipe(
            name='Build Basic Factory',
            description=basic_factory.description,
            recipe_type=RECIPE_TYPES.FACTORIES,
            consumes=bundle(
                funds=500000,
                items={energy: 12, copper: 30},
            ),
            produces=bundle(
                items={basic_factory: 1}
            ),
        )

        oil_combustion_plant = building(
            name='Oil Combustion Plant',
            description='A large, industrial-scale plant that burns oil to produce energy. Much more efficient and less polluting than burning oil by hand.',
            satisfaction_on_destroy=0,
            softcap=5,
            softcap_divider=5,
            consumes=bundle(
                items={oil: 8},
            ),
            produces=bundle(
                satisfaction=-2,
                items={energy: 12},
            ),
        )

        recipe(
            name='Build Oil Combustion Plant',
            description=oil_combustion_plant.description,
            recipe_type=RECIPE_TYPES.RESOURCE_CONVERSION,
            consumes=bundle(
                funds=500000,
                items={copper: 10, machinery_parts: 20},
            ),
            produces=bundle(
                items={oil_combustion_plant: 1}
            ),
        )

        basic_oil_well = building(
            name='Basic Oil Well',
            description='Inefficient, dirty as hell, and a horrible place to work, this well provides the black goo that runs the world.',
            satisfaction_on_destroy=1,
            softcap=10,
            softcap_divider=10,
            consumes=None,
            produces=bundle(
                satisfaction=-2,
                items={oil: 5}
            ),
        )

        recipe(
            name='Build Basic Oil Well',
            description=basic_oil_well.description,
            recipe_type=RECIPE_TYPES.RESOURCE_EXTRACTION,
            region=REGIONS_ANY.SADDLE_ARABIA,
            consumes=bundle(
                funds=200000,
            ),
            produces=bundle(
                items={basic_oil_well: 1}
            ),
        )

        basic_copper_mine = building(
            name='Basic Copper Mine',
            description='A nasty and downright dangerous place to work, this mine provides copper',
            satisfaction_on_destroy=1,
            softcap=10,
            softcap_divider=10,
            consumes=None,
            produces=bundle(
                satisfaction=-2,
                items={copper: 5}
            ),
        )

        recipe(
            name='Dig Basic Copper Mine',
            description=basic_copper_mine.description,
            recipe_type=RECIPE_TYPES.RESOURCE_EXTRACTION,
            region=REGIONS_ANY.ZEBRICA,
            consumes=bundle(
                funds=200000,
            ),
            produces=bundle(
                items={basic_copper_mine: 1}
            ),
        )

        basic_apple_farm = building(
            name='Basic Apple Farm',
            description='This Apple Farm uses nothing but pure horsepower, making it a backbreaking place to work for the local horses.',
            satisfaction_on_destroy=1,
            softcap=10,
            softcap_divider=10,
            consumes=None,
            produces=bundle(
                satisfaction=-2,
                items={apples: 5}
            ),
        )

        recipe(
            name='Plow Basic Apple Farm',
            description=basic_apple_farm.description,
            recipe_type=RECIPE_TYPES.RESOURCE_EXTRACTION,
            region=REGIONS_ANY.BURROZIL,
            consumes=bundle(
                funds=200000,
            ),
            produces=bundle(
                items={basic_apple_farm: 1}
            ),
        )

        mechanised_oil_well = building(
            name='Mechanised Oil Well',
            description='This oil well uses machinery and vehicles to more efficiently extract oil and make life easier on the Saddle Arabians who work there. It requires a little of energy to operate, but you should have plenty of that.',
            satisfaction_on_destroy=0,
            softcap=20,
            softcap_divider=5,
            consumes=bundle(
                items={energy: 1},
            ),
            produces=bundle(
                satisfaction=-1,
                items={oil: 8},
            ),
        )

        recipe(
            name='Upgrade Oil Well',
            description=mechanised_oil_well.description,
            recipe_type=RECIPE_TYPES.RESOURCE_EXTRACTION,
            region=REGIONS_ANY.SADDLE_ARABIA,
            consumes=bundle(
                funds=200000,
                items={copper: 5, vehicle_parts: 7, machinery_parts: 15, basic_oil_well: 1},
            ),
            produces=bundle(
                items={mechanised_oil_well: 1}
            ),
        )

        bakery = building(
            name='Bakery',
            description='This bakery produces pies, which are a staple of the >CLOP diet. Ponies will be satisfied just by watching the pies being made.',
            satisfaction_on_destroy=-5,
            consumes=bundle(
                items={energy: 1, apples: 2}
            ),
            produces=bundle(
                satisfaction=1,
                items={pies: 3}
            ),
        )

        recipe(
            name='Build Bakery',
            description=bakery.description,
            recipe_type=RECIPE_TYPES.SATISFACTION_BUILDINGS,
            consumes=bundle(
                funds=400000,
                items={energy: 10, copper: 5, vehicle_parts: 5, machinery_parts: 5},
            ),
            produces=bundle(
                items={bakery: 1}
            ),
        )

        print('Successfully seeded items database')

        # Update schedules
        update_items_name = 'Update items cache'
        update_items_defaults = dict(
            func='applications.items.tasks.update_cache',
            schedule_type=Schedule.MINUTES,
            minutes=10,
            repeats=-1,
            next_run=timezone.now(),
        )

        Schedule.objects.update_or_create(
            name=update_items_name,
            defaults=update_items_defaults,
        )

        tick_nations_name = 'Tick nations'
        tick_nations_defaults = dict(
            func='applications.nations.tasks.tick_nations',
            schedule_type=Schedule.CRON,
            # At the start of every second hour
            # cron='0 */2 * * *',
            cron='*/5 * * * *',
            repeats=-1,
        )
        Schedule.objects.update_or_create(
            name=tick_nations_name,
            defaults=tick_nations_defaults,
        )

        print('Successfully updated schedules')


