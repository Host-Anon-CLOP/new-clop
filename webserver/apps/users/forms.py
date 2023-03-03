from django import forms

from django.contrib.auth.forms import AuthenticationForm
from django.contrib.auth.forms import UserCreationForm
from django.core.exceptions import ValidationError
from django.utils.translation import gettext_lazy as _

from .models import User, UserProfile
from misc.validators import max_file_size


class LoginForm(AuthenticationForm):
    # def confirm_login_allowed(self, user):
    pass


class RegisterForm(UserCreationForm):
    email = forms.EmailField(max_length=254, required=False)

    class Meta:
        model = User
        fields = ('username', 'email', 'password1', 'password2')


class ChangeEmailForm(forms.ModelForm):
    error_messages = {
        "password_incorrect": _(
            "Your old password was entered incorrectly. Please enter it again."
        ),
    }
    old_password = forms.CharField(label=_("Old password"), strip=False)
    email = forms.EmailField(max_length=254, required=False)

    class Meta:
        model = User
        fields = ('email',)

    def clean_old_password(self):
        old_password = self.cleaned_data["old_password"]
        if not self.instance.check_password(old_password):
            raise ValidationError(
                self.error_messages["password_incorrect"],
                code="password_incorrect",
            )
        return old_password


class UserProfileForm(forms.ModelForm):
    bio = forms.CharField(required=False)
    flag = forms.ImageField(required=False, validators=[max_file_size(1)])

    color_scheme = forms.ChoiceField(choices=UserProfile.COLOR_SCHEMES.choices, required=False)
    hide_banners = forms.BooleanField(required=False)

    class Meta:
        model = UserProfile
        fields = ('bio', 'flag', 'color_scheme', 'hide_banners')
