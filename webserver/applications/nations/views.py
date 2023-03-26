from django.contrib import messages
from django.contrib.auth.mixins import LoginRequiredMixin, UserPassesTestMixin
from django.shortcuts import redirect
from django.urls import reverse_lazy
from django.views.generic import CreateView, TemplateView, UpdateView, View

from misc.cached import get_all_recipes
from misc.errors import exception_to_message, InvalidInput
from misc.views import HasNationMixin

from .forms import CreateNationForm, EditNationForm
from .models import NationRecipe, NationBuilding


class CreateNationView(LoginRequiredMixin, UserPassesTestMixin, CreateView):
    template_name = 'nations/create_nation.html'
    success_url = reverse_lazy('nation_overview')
    form_class = CreateNationForm

    def test_func(self):
        # Disallow users with nations from creating new ones
        return not self.request.user.has_nations

    def form_valid(self, form):
        form.instance.owner = self.request.user
        return super().form_valid(form)


class NationOverview(HasNationMixin, UpdateView):
    template_name = 'nations/overview.html'
    form_class = EditNationForm
    success_url = reverse_lazy('nation_overview')

    def get_object(self, queryset=None):
        return self.request.user.nation


class BuildingActionView(HasNationMixin, View):
    def post(self, request, *args, **kwargs):
        building_id = kwargs['building_id']
        amount = int(request.POST['amount'])

        nation = request.user.nation

        with exception_to_message(request):
            try:
                building = nation.buildings.get(id=building_id)
            except NationBuilding.DoesNotExist:
                raise InvalidInput("Building does not exist")

            if 'disable' in request.POST:
                building.disable(amount)
                messages.success(request, f'Disabled {amount} of {building.name}')
            elif 'enable' in request.POST:
                building.enable(amount)
                messages.success(request, f'Enabled {amount} of {building.name}')
            elif 'destroy' in request.POST:
                satisfaction = building.destroy(amount)
                messages.success(request, f'Destroyed {amount} of {building.name} and gained {satisfaction} satisfaction')
            else:
                raise InvalidInput("Unknown action")

        return redirect('nation_overview')


class NationActionsView(HasNationMixin, TemplateView):
    template_name = 'nations/actions.html'


class RecipeBuyView(HasNationMixin, View):
    def post(self, request, *args, **kwargs):
        data = request.POST
        recipe_id = int(kwargs['recipe_id'])
        amount = int(data['amount'])

        nation = request.user.nation
        recipe = NationRecipe.no_prefetch.get(id=recipe_id)
        recipe.update_from_cache(recipe_amount=amount)

        with exception_to_message(request):
            nation.buy_recipe(recipe)

        return redirect('nation_actions')
