from django.conf import settings
from django.contrib import admin
from django.urls import include, path
from django.views.generic import TemplateView, RedirectView

urlpatterns = [
    path('', TemplateView.as_view(template_name="layout.html")),
    path('auth/', include('applications.users.auth_urls')),
    path('user/', include('applications.users.user_urls')),
    path('nation/', include('applications.nations.urls')),
    path('market/', include('applications.markets.urls')),
    path('alliance/', include('applications.alliances.urls')),
    path('notifications/', include('applications.notifications.urls')),

    # redirect admin login to auth/login
    path('admin/login/', RedirectView.as_view(url='/auth/login/', permanent=True)),
    path('admin/', admin.site.urls),
]

admin.site.site_header = 'CLOP Administration'
admin.site.site_title = 'CLOP Administration'
admin.site.index_title = 'CLOP Administration'


if 'debug_toolbar' in settings.INSTALLED_APPS:
    import debug_toolbar
    urlpatterns = [
        path('__debug__/', include(debug_toolbar.urls)),
    ] + urlpatterns
