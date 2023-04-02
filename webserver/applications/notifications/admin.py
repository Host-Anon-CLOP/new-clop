from django.contrib import admin
from django.utils.translation import gettext_lazy as _

from .models import NationReport


@admin.action(description='Mark as read')
def mark_as_read(modeladmin, request, queryset):
    queryset.update(read=True)


@admin.action(description='Mark as unread')
def mark_as_unread(modeladmin, request, queryset):
    queryset.update(read=False)


@admin.register(NationReport)
class NationReportAdmin(admin.ModelAdmin):
    search_fields = ('nation__name',)
    list_filter = ('report_type',)
    list_display = ('nation', 'report_type', 'created_on', 'read',)
    actions = (mark_as_read, mark_as_unread,)
