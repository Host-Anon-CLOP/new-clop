from django.urls import path

from .views import ReportsView, DismissReportView, DismissAllReportsView

urlpatterns = [
    path('reports/', ReportsView.as_view(), name='reports'),
    path('report/dismiss/<int:report_id>/', DismissReportView.as_view(), name='dismiss_report'),
    path('report/dismiss_all/', DismissAllReportsView.as_view(), name='dismiss_all_reports'),
]
