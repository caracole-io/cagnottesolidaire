"""Utilities for the Cagnotte Solidaire django application."""
from django.contrib.auth.mixins import UserPassesTestMixin


class IsUserOrAboveMixin(UserPassesTestMixin):
    """Mixin to check a user can access to a View."""

    def test_func(self):
        """Check that the user has the right for a task."""
        if not self.request.user.is_authenticated:
            return False
        if self.request.user.is_staff:
            return True
        return self.get_user() == self.request.user
