from django.db import models


class Nation(models.Model):
    owner = models.ForeignKey('users.User', on_delete=models.CASCADE, related_name='nations')

    name = models.CharField(max_length=50, blank=False, unique=True)
    description = models.TextField(max_length=1000, blank=True)

    created_on = models.DateTimeField(auto_now_add=True)
    age = models.PositiveIntegerField(default=0)

    funds = models.BigIntegerField(default=500000)
    gdp_last_turn = models.PositiveBigIntegerField(default=0)
    satisfaction = models.IntegerField(default=0)

    se_relation = models.IntegerField(default=0)
    nlr_relation = models.IntegerField(default=0)

    class REGIONS(models.IntegerChoices):
        BURROZIL = (1, 'Burrozil')
        ZEBRICA = (2, 'Zebrica')
        SADDLE_ARABIA = (3, 'Saddle Arabia')
        PRZEWALSKIA = (4, 'Przewalskia')

    region = models.PositiveSmallIntegerField(choices=REGIONS.choices)

    class SUBREGIONS(models.IntegerChoices):
        NORTH = (1, 'North')
        CENTRAL = (2, 'Central')
        SOUTH = (3, 'South')

    subregion = models.PositiveSmallIntegerField(choices=SUBREGIONS.choices)


    # class GOVERNMENTS(models.IntegerChoices):
    #     LOOSE_DESPOTISM = (1, 'Loose Despotism')
    #     DEMOCRACY = (2, 'Democracy')

