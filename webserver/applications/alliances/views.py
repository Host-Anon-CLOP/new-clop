from django.shortcuts import render
from django.views.generic import TemplateView

from .models import Alliance

from misc.views import HasAllianceMixin


class AlliancesListView(TemplateView):
    template_name = 'alliances/alliances.html'

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        alliances = list(Alliance.objects.all().prefetch_related('members',))
        alliances = sorted(alliances, key=lambda alliance: alliance.active_members, reverse=True)
        context['alliances'] = alliances
        return context


class AlliancePublicView(TemplateView):
    template_name = 'alliances/alliance_public.html'

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context['alliance'] = Alliance.objects.prefetch_related('members', 'members__user').get(pk=kwargs['alliance_id'])
        return context


class MyAllianceView(HasAllianceMixin, TemplateView):
    template_name = 'alliances/my_alliance.html'

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        alliance_id = self.request.user.alliance.alliance_id
        context['alliance'] = Alliance.objects.prefetch_related('members', 'members__user').get(pk=alliance_id)
        return context
