from django.urls import path

from .views import UpdateUserProfileVIew

urlpatterns = [
    path('', UpdateUserProfileVIew.as_view(), name='profile'),
]