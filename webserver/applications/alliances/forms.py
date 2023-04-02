from django import forms

from misc.files import max_file_size

from .models import Alliance


class CreateAllianceForm(forms.ModelForm):
    flag = forms.ImageField(required=False, validators=[max_file_size(1)])

    class Meta:
        model = Alliance
        fields = ('name', 'description', 'flag', )


class EditAllianceForm(forms.ModelForm):
    flag = forms.ImageField(required=False, validators=[max_file_size(1)])

    class Meta:
        model = Alliance
        fields = ('description', 'flag', )
