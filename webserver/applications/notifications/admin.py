from django.contrib import admin
from django.utils.translation import gettext_lazy as _

from .models import NationReport


@admin.register(NationReport)
class NationReportAdmin(admin.ModelAdmin):
    pass
