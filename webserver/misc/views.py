from django.contrib.auth.mixins import LoginRequiredMixin, UserPassesTestMixin


class HasNationMixin(LoginRequiredMixin, UserPassesTestMixin):
    def test_func(self):
        # Disallow users with nations from creating new ones
        return self.request.user.has_nations
