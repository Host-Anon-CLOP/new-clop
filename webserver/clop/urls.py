from django.urls import path, include
from django.conf import settings

from django.contrib import admin
from django.views.generic import TemplateView


urlpatterns = [
    path('', TemplateView.as_view(template_name="layout.html")),  # this is new
    path('auth/', include('apps.users.auth_urls')),
    path('user/', include('apps.users.user_urls')),
    path('admin/', admin.site.urls),
]

if settings.DEBUG:
    import debug_toolbar
    urlpatterns = [
        path('__debug__/', include(debug_toolbar.urls)),
    ] + urlpatterns
