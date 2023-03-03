from django import forms

from .models import Nation


class CreateNationForm(forms.ModelForm):
    class Meta:
        model = Nation
        fields = ('name', 'description', 'region', 'subregion', )
