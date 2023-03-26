from django.contrib import messages
from django.contrib.auth.mixins import LoginRequiredMixin, UserPassesTestMixin
from django.core.exceptions import PermissionDenied
from django.http import HttpResponse
from django.shortcuts import redirect
from django.views.generic import View, TemplateView

from .models import NationReport
from misc.views import HasNationMixin


class ReportsView(HasNationMixin, TemplateView):
    template_name = 'nations/reports.html'

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context['show_reports'] = False

        nation = self.request.user.nation
        reports = NationReport.objects.filter(nation=nation)

        if report_type := self.request.GET.get('report_type', None):
            reports = reports.filter(report_type=report_type)
        context['nation_reports'] = reports

        return context


class DismissReportView(LoginRequiredMixin, View):
    def post(self, request, *args, **kwargs):
        report_id = kwargs.get('report_id')
        report = NationReport.objects.get(pk=report_id)
        if report.nation.owner_id != request.user.id:
            raise PermissionDenied()

        report.mark_read()

        next_url = request.POST.get('next', None)
        if next_url:
            return redirect(next_url)
        return HttpResponse(status=204)


class DismissAllReportsView(LoginRequiredMixin, View):
    def post(self, request, *args, **kwargs):
        reports = NationReport.objects.filter(nation__owner=request.user)
        reports.update(read=True)

        next_url = request.POST.get('next', None)
        if next_url:
            return redirect(next_url)

        return HttpResponse(status=204)

