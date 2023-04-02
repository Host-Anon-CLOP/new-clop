from django.urls import path

from .views import AlliancesListView, AlliancePublicView, CreateAllianceView, MyAllianceView, ChangeMemberRankView, JoinAllianceView


urlpatterns = [
    path('all/', AlliancesListView.as_view(), name='alliances'),
    path('my/', MyAllianceView.as_view(), name='my_alliance'),
    path('my/member/<int:member_id>/change_rank/', ChangeMemberRankView.as_view(), name='change_rank'),
    path('create/', CreateAllianceView.as_view(), name='create_alliance'),
    path('<int:alliance_id>/', AlliancePublicView.as_view(), name='alliance'),
    path('<int:alliance_id>/join/', JoinAllianceView.as_view(), name='join_alliance'),
]
