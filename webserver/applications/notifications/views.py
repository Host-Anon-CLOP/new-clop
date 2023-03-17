from django.contrib import messages
from django.contrib.auth.mixins import LoginRequiredMixin, UserPassesTestMixin
from django.http import HttpResponse
from django.views.generic import View
from django.core.exceptions import PermissionDenied


from .models import NationReport


class DismissReportView(LoginRequiredMixin, View):
    def post(self, request, *args, **kwargs):
        report_id = kwargs.get('report_id')
        report = NationReport.objects.get(pk=report_id)
        if report.nation.owner != request.user:
            raise PermissionDenied()

        report.mark_read()

        return HttpResponse(status=204)
