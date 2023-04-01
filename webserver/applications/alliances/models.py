import uuid

from django.db import models
from django.urls import reverse
from django.utils.functional import cached_property

from misc.errors import InvalidInput

from applications.nations.models import Nation
from misc.files import PathAndRename


flag_upload = PathAndRename('alliance_flags')
banner_upload = PathAndRename('alliance_banners')


class ALLIANCE_RANKS(models.IntegerChoices):
    LEADER = 1, 'Leader'
    SECOND_IN_COMMAND = 2, 'Second in Command'
    GENERAL = 4, 'General'
    OFFICER = 5, 'Officer'
    QUARTERMASTER = 6, 'Quartermaster'
    SENIOR = 10, 'Senior Member'
    MEMBER = 100, 'Member'


class Alliance(models.Model):
    name = models.CharField(max_length=50)
    description = models.TextField(blank=True)
    flag = models.ImageField(upload_to=flag_upload, blank=True, null=True)
    banner = models.ImageField(upload_to=banner_upload, blank=True, null=True)

    created_at = models.DateTimeField(auto_now_add=True)  #todo rename

    def __str__(self):
        return self.name

    def get_absolute_url(self):
        return reverse('alliance', kwargs={'alliance_id': self.pk})

    @cached_property
    def leader(self):
        return self.members.filter(rank=ALLIANCE_RANKS.LEADER).first()

    @cached_property
    def second_in_command(self):
        return self.members.filter(rank=ALLIANCE_RANKS.SECOND_IN_COMMAND).first()

    @cached_property
    def active_members(self):
        return self.members.count()

    @cached_property
    def active_nations(self):
        return Nation.objects.filter(owner__alliance__alliance_id=self.pk).count()


class AllianceMember(models.Model):
    user = models.OneToOneField('users.User', on_delete=models.CASCADE, related_name='alliance')
    alliance = models.ForeignKey(Alliance, on_delete=models.CASCADE, related_name='members')

    joined_at = models.DateTimeField(auto_now_add=True)

    rank = models.PositiveSmallIntegerField(choices=ALLIANCE_RANKS.choices, default=ALLIANCE_RANKS.MEMBER)

    class Meta:
        ordering = ['rank', 'joined_at']

    def __str__(self):
        return f'{self.user.username} in {self.alliance.name} ({self.get_rank_display()})'

    def save(
        self, force_insert=False, force_update=False, using=None, update_fields=None
    ):
        if self.rank == ALLIANCE_RANKS.LEADER:
            if self.alliance.leader:
                raise InvalidInput('Only one leader per alliance')

        if self.rank == ALLIANCE_RANKS.SECOND_IN_COMMAND:
            if self.alliance.second_in_command:
                raise InvalidInput('Only one second in command per alliance')

        super().save(force_insert, force_update, using, update_fields)

    def delete(self, using=None, keep_parents=False):
        if self.rank == ALLIANCE_RANKS.LEADER:
            self.alliance.second_in_command.rank = ALLIANCE_RANKS.LEADER

        super().delete(using, keep_parents)

    @property
    def nations(self):
        return self.user.nations

    @property
    def can_edit_info(self):
        return self.rank <= ALLIANCE_RANKS.OFFICER


class AllianceApplication(models.Model):
    user = models.ForeignKey('users.User', on_delete=models.CASCADE, related_name='alliance_applications')
    alliance = models.ForeignKey(Alliance, on_delete=models.CASCADE, related_name='applications')

    message = models.TextField(blank=True)

    created_at = models.DateTimeField(auto_now_add=True)

    class Meta:
        ordering = ['created_at']

    def __str__(self):
        return f'{self.user.username} in {self.alliance.name}'
