from django.urls import path

from .views import (
    BuildingActionView,
    CreateNationView,
    NationActionsView,
    NationOverview,
    RecipeBuyView,
)

urlpatterns = [
    path('', NationOverview.as_view(), name='nation_overview'),
    path('create/', CreateNationView.as_view(), name='create_nation'),
    path('building/<int:building_id>/action/', BuildingActionView.as_view(), name='building_action'),
    path('actions/', NationActionsView.as_view(), name='nation_actions'),
    path('actions/recipe/<int:recipe_id>/', RecipeBuyView.as_view(), name='recipe_buy'),
]