from django.urls import path

from .views import \
    LoginView, \
    LogoutView, \
    RegisterView, \
    ChangePasswordView, \
    ForgotPasswordView, \
    PasswordResetView, \
    ChangeEmailView

urlpatterns = [
    path('login/', LoginView.as_view(), name='login'),
    path('logout/', LogoutView.as_view(), name='logout'),
    path('register/', RegisterView.as_view(), name='register'),
    path('change-password', ChangePasswordView.as_view(), name='change-password'),
    path('forgot-password/', ForgotPasswordView.as_view(), name='forgot-password'),
    path('reset-password/<uidb64>/<token>/', PasswordResetView.as_view(), name='reset-password'),
    path('change-email', ChangeEmailView.as_view(), name='change-email'),
]