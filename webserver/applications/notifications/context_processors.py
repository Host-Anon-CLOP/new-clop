from django.conf import settings

from .models import REPORT_TYPES, NationReport


def reports(request):
    if not request.user.is_authenticated:
        return {}

    user_nation_ids = request.user.nations.values_list('id', flat=True)
    report_query = NationReport.objects.filter(nation_id__in=user_nation_ids, read=False)
    report_query = report_query.order_by('-created_at')
    report_query = report_query.select_related('nation__owner')
    report_query = report_query[:settings.REPORTS_DISPLAY_LIMIT]

    return {
        'reports': report_query,
        'REPORT_TYPES': {x.name: x.value for x in REPORT_TYPES},
        'show_reports': True,
    }
