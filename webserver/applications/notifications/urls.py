from django.urls import path

from .views import DismissReportView

urlpatterns = [
    path('report/dismiss/<int:report_id>/', DismissReportView.as_view(), name='dismiss_report'),
]