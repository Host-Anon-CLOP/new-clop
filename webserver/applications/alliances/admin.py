from django.contrib import admin

from .models import Alliance, AllianceMember


class AllianceMemberInline(admin.TabularInline):
    model = AllianceMember
    fk_name = 'alliance'
    extra = 1
    fields = ('user', 'rank', 'joined_on', )
    readonly_fields = ('joined_on', )


@admin.register(Alliance)
class AllianceAdmin(admin.ModelAdmin):
    list_display = ('name', 'leader', 'second_in_command', 'created_on', )
    search_fields = ('name', )
    inlines = (AllianceMemberInline, )

    def leader(self, obj):
        return obj.leader

    def second_in_command(self, obj):
        return obj.second_in_command
