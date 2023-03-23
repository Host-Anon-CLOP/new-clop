from django.urls import path

from .views import DismissReportView, DismissAllReportsView

urlpatterns = [
    path('report/dismiss/<int:report_id>/', DismissReportView.as_view(), name='dismiss_report'),
    path('report/dismiss_all/', DismissAllReportsView.as_view(), name='dismiss_all_reports'),
]
