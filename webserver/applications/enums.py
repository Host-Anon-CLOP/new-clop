from django.db import models


class REGIONS(models.IntegerChoices):
    BURROZIL = (1, 'Burrozil')
    ZEBRICA = (2, 'Zebrica')
    SADDLE_ARABIA = (3, 'Saddle Arabia')
    PRZEWALSKIA = (4, 'Przewalskia')


class REGIONS_ANY(models.IntegerChoices):
    ANY = (0, 'Any')
    BURROZIL = (1, 'Burrozil')
    ZEBRICA = (2, 'Zebrica')
    SADDLE_ARABIA = (3, 'Saddle Arabia')
    PRZEWALSKIA = (4, 'Przewalskia')


class SUBREGIONS(models.IntegerChoices):
    NORTH = (1, 'North')
    CENTRAL = (2, 'Central')
    SOUTH = (3, 'South')


class SUBREGIONS_ANY(models.IntegerChoices):
    ANY = (0, 'Any')
    NORTH = (1, 'North')
    CENTRAL = (2, 'Central')
    SOUTH = (3, 'South')


class RECIPE_TYPES(models.IntegerChoices):
    BASIC_ACTIONS = (1, 'Basic Actions')
    RESOURCE_EXTRACTION = (2, 'Resource Extraction')
    RESOURCE_CONVERSION = (3, 'Resource Conversion')
    SATISFACTION_BUILDINGS = (4, 'Satisfaction Buildings')
    FACTORIES = (5, 'Factories')
    MANUFACTURING = (6, 'Manufacturing')
    MILITARY = (7, 'Military')
    SUPERPOWER_RELATIONS = (8, 'Superpower Relations')
    SPECIAL = (9, 'Special')

# class GOVERNMENTS(models.IntegerChoices): model?
#     LOOSE_DESPOTISM = (1, 'Loose Despotism')
#     DEMOCRACY = (2, 'Democracy')
