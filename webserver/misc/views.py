from django.contrib.auth.mixins import LoginRequiredMixin, UserPassesTestMixin


class HasNationMixin(LoginRequiredMixin, UserPassesTestMixin):
    def test_func(self):
        return self.request.user.has_nations


class HasAllianceMixin(LoginRequiredMixin, UserPassesTestMixin):
    def test_func(self):
        return self.request.user.has_alliance
