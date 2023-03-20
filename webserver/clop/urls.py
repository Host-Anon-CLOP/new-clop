from django.conf import settings
from django.contrib import admin
from django.urls import include, path
from django.views.generic import TemplateView

urlpatterns = [
    path('', TemplateView.as_view(template_name="layout.html")),  # this is new
    path('auth/', include('applications.users.auth_urls', namespace='auth')),
    path('user/', include('applications.users.user_urls', namespace='users')),
    path('nation/', include('applications.nations.urls', namespace='nations')),

    path('notifications/', include('applications.notifications.urls')),
    path('admin/', admin.site.urls),
]

if settings.DEBUG:
    import debug_toolbar
    urlpatterns = [
        path('__debug__/', include(debug_toolbar.urls)),
    ] + urlpatterns
