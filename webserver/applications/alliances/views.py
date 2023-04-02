from django.contrib.auth.mixins import UserPassesTestMixin, LoginRequiredMixin
from django.core.exceptions import PermissionDenied
from django.shortcuts import render, redirect
from django.urls import reverse_lazy
from django.views import View
from django.views.generic import TemplateView, FormView, CreateView

from .forms import EditAllianceForm, CreateAllianceForm
from .models import Alliance, ALLIANCE_RANKS, AllianceMember

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


class CreateAllianceView(LoginRequiredMixin, UserPassesTestMixin, CreateView):
    template_name = 'alliances/create_alliance.html'
    success_url = reverse_lazy('my_alliance')
    form_class = CreateAllianceForm

    def test_func(self):
        # Disallow users with alliance from creating new ones
        return not self.request.user.has_alliance

    def form_valid(self, form):
        alliance = form.instance
        result = super().form_valid(form)

        member = AllianceMember.objects.create(user=self.request.user, alliance=alliance, rank=ALLIANCE_RANKS.LEADER)
        member.save()

        return result


class MyAllianceView(HasAllianceMixin, TemplateView):
    template_name = 'alliances/my_alliance.html'

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        member = self.request.user.alliance
        alliance_id = member.alliance_id
        alliance = Alliance.objects.prefetch_related('members', 'members__user').get(pk=alliance_id)
        context['my_member'] = member
        context['alliance'] = alliance
        context['ranks'] = ALLIANCE_RANKS

        if member.can_edit_info:
            if self.request.method == 'POST' and 'edit' in self.request.POST:
                context['edit_form'] = EditAllianceForm(self.request.POST, self.request.FILES, instance=alliance)
            else:
                context['edit_form'] = EditAllianceForm(instance=alliance)

        return context

    def post(self, request, *args, **kwargs):
        context = self.get_context_data(**kwargs)

        if 'edit' in request.POST:
            form = context['edit_form']

            if form.is_valid():
                form.save()

        return self.render_to_response(context)


class ChangeMemberRankView(HasAllianceMixin, View):
    def test_func(self):
        return super().test_func() and self.request.user.alliance.rank <= ALLIANCE_RANKS.OFFICER

    def post(self, request, *args, **kwargs):
        my_member = self.request.user.alliance
        member = AllianceMember.objects.get(user_id=kwargs['member_id'], alliance_id=my_member.alliance_id)
        new_rank = int(request.POST['rank'])

        if my_member.rank >= member.rank:
            raise PermissionDenied('You cannot change the rank of a member with a higher or equal rank than you.')

        if new_rank <= my_member.rank:
            raise PermissionDenied('You cannot change the rank of a member to a rank higher or equal to yours.')

        member.rank = new_rank
        member.save()

        return redirect('my_alliance')


class JoinAllianceView(LoginRequiredMixin, UserPassesTestMixin, View):
    def test_func(self):
        # Disallow users with alliance from joining another one
        return not self.request.user.has_alliance

    def post(self, request, *args, **kwargs):
        alliance = Alliance.objects.get(pk=kwargs['alliance_id'])
        alliance.applications.create(user=request.user)
        return redirect('alliance', alliance_id=alliance.id)

