from django.shortcuts import render
from django.views.generic import CreateView
from django.contrib.auth.mixins import LoginRequiredMixin

from .forms import CreateNationForm


class CreateNationView(LoginRequiredMixin, CreateView):
    form_class = CreateNationForm

    def form_valid(self, form):
        form.instance.user = self.request.user
        return super().form_valid(form)




