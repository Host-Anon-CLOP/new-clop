from django import forms

from misc.files import max_file_size

from .models import Nation


class CreateNationForm(forms.ModelForm):
    flag = forms.ImageField(required=False, validators=[max_file_size(1)])

    class Meta:
        model = Nation
        fields = ('name', 'description', 'flag', 'region', 'subregion', )


class EditNationForm(forms.ModelForm):
    flag = forms.ImageField(required=False, validators=[max_file_size(1)])

    class Meta:
        model = Nation
        fields = ('description', 'flag', )
