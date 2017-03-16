from django.test import TestCase


class TestProjet(TestCase):
    def setUp(self):
        a, b, c = (User.objects.create_user(guy, email=f'{guy}@example.org', password=guy) for guy in 'abc')
