from django.core.cache import cache
from django_q.tasks import async_task

from .models import Nation


def tick_nations():
    # todo filter stasis
    nation_ids = Nation.objects.values_list('id', flat=True)
    for nation_id in nation_ids:
        async_task(tick_nation, nation_id)


def tick_nation(nation_id):
    nation = Nation.objects.get(id=nation_id)
    nation.tick()
    nation.save()
