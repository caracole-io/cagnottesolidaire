from django.contrib.auth.mixins import UserPassesTestMixin


class IsUserOrAboveMixin(UserPassesTestMixin):
    def test_func(self):
        if not self.request.user.is_authenticated:
            return False
        if self.request.user.is_staff:
            return True
        return self.get_user() == self.request.user
