from django.contrib import messages
from django.contrib.auth import login
from django.contrib.auth import views as auth_views
from django.contrib.auth.decorators import login_required
from django.contrib.auth.mixins import LoginRequiredMixin
from django.shortcuts import redirect
from django.urls import reverse_lazy
from django.utils.decorators import method_decorator
from django.views.decorators.csrf import csrf_protect
from django.views.decorators.debug import sensitive_post_parameters
from django.views.generic import CreateView, UpdateView

from .models import Login

from .forms import ChangeEmailForm, LoginForm, RegisterForm, UserProfileForm


def get_ip_address(request):
    forwarded = request.META.get('HTTP_X_FORWARDED_FOR')
    if forwarded:
        return forwarded.split(',')[0]
    else:
        return request.META.get('REMOTE_ADDR')


class LoginView(auth_views.LoginView):
    template_name = 'users/login.html'
    redirect_authenticated_user = True
    form_class = LoginForm

    def form_valid(self, form):
        result = super().form_valid(form)
        Login.objects.create(
            user=self.request.user,
            ip=get_ip_address(self.request),
        )

        messages.success(self.request, 'Successfully logged in.')
        return result


class LogoutView(auth_views.LogoutView):
    def dispatch(self, request, *args, **kwargs):
        result = super().dispatch(request, *args, **kwargs)
        messages.info(request, 'Logged out.')
        return result


class RegisterView(CreateView):
    template_name = 'users/register.html'
    success_url = reverse_lazy('create_nation')
    form_class = RegisterForm

    def form_valid(self, form):
        ip = get_ip_address(self.request)
        form.instance.register_ip = ip
        user = form.save()

        login(self.request, user)
        Login.objects.create(
            user=self.request.user,
            ip=ip,
        )

        messages.success(self.request, 'Successfully registered. Welcome to >CLOP, fag.')
        return redirect(self.success_url)


class ChangePasswordView(auth_views.PasswordChangeView):
    template_name = 'users/change_password.html'
    success_url = '/'

    def form_valid(self, form):
        result = super().form_valid(form)
        messages.success(self.request, 'Password successfully changed.')
        return result


class ForgotPasswordView(auth_views.PasswordResetView):
    template_name = 'users/forgot_password.html'
    email_template_name = 'users/reset_password_email.html'
    subject_template_name = 'users/reset_password_subject.txt'
    success_url = '/'

    def form_valid(self, form):
        result = super().form_valid(form)
        messages.info(self.request, 'Sent email with reset instructions if it exists.')
        return result


class PasswordResetView(auth_views.PasswordResetConfirmView):
    template_name = 'users/reset_password.html'
    success_url = reverse_lazy('profile')
    post_reset_login = True

    def form_valid(self, form):
        result = super().form_valid(form)
        messages.success(self.request, 'Password successfully changed.')
        return result


class ChangeEmailView(LoginRequiredMixin, UpdateView):
    template_name = 'users/change_email.html'
    success_url = reverse_lazy('profile')
    form_class = ChangeEmailForm

    @method_decorator(sensitive_post_parameters())
    @method_decorator(csrf_protect)
    @method_decorator(login_required)
    def dispatch(self, *args, **kwargs):
        return super().dispatch(*args, **kwargs)

    def get_object(self, queryset=None):
        return self.request.user

    def form_valid(self, form):
        result = super().form_valid(form)
        messages.success(self.request, 'Email successfully changed.')
        return result


class UpdateUserProfileVIew(LoginRequiredMixin, UpdateView):
    template_name = 'users/profile_edit.html'
    success_url = reverse_lazy('profile')
    form_class = UserProfileForm

    def get_object(self, queryset=None):
        return self.request.user.profile

    def form_valid(self, form):
        result = super().form_valid(form)
        messages.success(self.request, 'Profile successfully updated.')
        return result
