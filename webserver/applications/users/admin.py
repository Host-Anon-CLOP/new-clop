from django.contrib import admin
from django.contrib.auth.admin import UserAdmin
from django.utils.translation import gettext_lazy as _

from applications.nations.models import Nation

from applications.alliances.models import AllianceMember

from .models import User, UserProfile


class UserProfileInline(admin.StackedInline):
    verbose_name_plural = 'Profile'
    model = UserProfile
    can_delete = False
    fk_name = 'user'
    min_num = 1
    max_num = 1

    def get_formset(self, request, obj=None, **kwargs):
        formset = super().get_formset(request, obj, **kwargs)
        # limit active nations to those owned by the user
        formset.form.base_fields['active_nation'].queryset = Nation.objects.filter(owner_id=obj.pk)
        return formset


class AllianceMemberInline(admin.TabularInline):
    verbose_name_plural = 'Alliance Membership'
    model = AllianceMember
    fields = ('alliance', 'rank', 'joined_at', )
    readonly_fields = ('joined_at', )
    min_num = 0
    max_num = 1


class NationInline(admin.TabularInline):
    model = Nation
    extra = 1
    fields = ('name', 'region', 'subregion', 'funds', 'satisfaction', 'se_relation', 'nlr_relation', )
    show_change_link = True


@admin.register(User)
class UserAdmin(UserAdmin):
    inlines = (UserProfileInline, AllianceMemberInline, NationInline)

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
