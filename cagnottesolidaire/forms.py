from django.contrib.auth.models import User
from registration.forms import RegistrationFormUniqueEmail


class RegistrationFormFullName(RegistrationFormUniqueEmail):
    class Meta:
        model = User
        fields = ("username", "first_name", "last_name", "email")
