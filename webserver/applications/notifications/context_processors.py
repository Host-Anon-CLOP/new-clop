from django.conf import settings

from .models import NationReport, REPORT_TYPES


def reports(request):
    if not request.user.is_authenticated:
        return {}

    user_nation_ids = request.user.nations.values_list('id', flat=True)
    reports = NationReport.objects.filter(nation_id__in=user_nation_ids, read=False).order_by('-created_at')[:settings.REPORTS_DISPLAY_LIMIT]

    return {
        'reports': reports,
        'REPORT_TYPES': {x.name: x.value for x in REPORT_TYPES}
    }
