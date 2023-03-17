from django.contrib import admin
from django.contrib.auth.admin import UserAdmin
from django.utils.translation import gettext_lazy as _

from applications.nations.models import Nation

from .models import User, UserProfile


class UserProfileInline(admin.StackedInline):
    verbose_name_plural = 'Profile'
    model = UserProfile
    can_delete = False
    fk_name = 'user'
    min_num = 1
    max_num = 1


class NationInline(admin.TabularInline):
    model = Nation
    extra = 1
    fields = ('name', 'region', 'subregion', 'funds', 'satisfaction', 'se_relation', 'nlr_relation', )


@admin.register(User)
class UserAdmin(UserAdmin):
    inlines = (UserProfileInline, NationInline)

    fieldsets = (
        (None, {'fields': ('username', 'password')}),
        (_('Personal info'), {'fields': ('email', 'register_ip', )}),
        (_('Permissions'),
            {
                'classes': ('collapse',),
                'fields': (
                    'is_active',
                    'is_staff',
                    'is_superuser',
                    'groups',
                    'user_permissions',
                ),
            },
        ),
        (_('Important dates'), {'fields': ('last_login', 'date_joined')}),
    )
    list_display = ('username', 'email', 'register_ip', 'is_staff', )
    search_fields = ('username', 'email', 'register_ip', )
