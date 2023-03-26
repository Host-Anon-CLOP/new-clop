from django.conf import settings
from django.contrib import messages
from django.db import models, transaction
from django.db.models import Q


class REPORT_TYPES(models.IntegerChoices):
    RECIPE = (1, 'Recipe')
    DESTROY = (2, 'Destroy')
    TICK = (3, 'Tick')
    MARKET = (4, 'Market')
    # todo attacks etc


class NationReport(models.Model):
    created_at = models.DateTimeField(auto_now_add=True)
    nation = models.ForeignKey('nations.Nation', on_delete=models.CASCADE, related_name='reports')

    text = models.TextField()
    details = models.TextField(blank=True)

    report_type = models.PositiveSmallIntegerField(choices=REPORT_TYPES.choices)

    read = models.BooleanField(default=False)

    class Meta:
        ordering = ['-created_at']

    def save(
        self, force_insert=False, force_update=False, using=None, update_fields=None
    ):
        super().save(force_insert, force_update, using, update_fields)

        # delete more than LIMIT oldest reports
        query = self.nation.reports.filter(~Q(id=self.id)).filter(nation_id=self.nation_id, report_type=self.report_type)

        ids = query.order_by('-created_at')[settings.REPORTS_LIMIT:].values_list('pk', flat=True)
        self.nation.reports.filter(pk__in=ids).delete()

    def mark_read(self):
        self.read = True
        self.save()
