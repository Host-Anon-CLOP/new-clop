from django.urls import path

from .views import AlliancesListView, AlliancePublicView, MyAllianceView


urlpatterns = [
    path('all/', AlliancesListView.as_view(), name='alliances'),
    path('my/', MyAllianceView.as_view(), name='my_alliance'),
    path('<int:alliance_id>/', AlliancePublicView.as_view(), name='alliance'),
]
