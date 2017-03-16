from django.test import TestCase
from django.contrib.auth.models import User
from django.core.urlresolvers import reverse

from .models import Projet


class TestProjet(TestCase):
    def setUp(self):
        a, b, c = (User.objects.create_user(guy, email=f'{guy}@example.org', password=guy) for guy in 'abc')

    def test_projet(self):
        self.assertEqual(Projet.objects.count(), 0)
        self.assertEqual(self.client.get(reverse('projets:projet', kwargs={'slug': 'first'})).status_code, 404)
        self.assertEqual(self.client.get(reverse('projets:projet_list')).status_code, 200)
        self.assertEqual(self.client.get(reverse('projets:projet_create')).status_code, 302)
        self.client.login(username='a', password='a')
        self.assertEqual(self.client.get(reverse('projets:projet_create')).status_code, 200)
        projet_data = {'nom': 'first', 'objectif': 'nothing', 'finances': 42,
                       'fin_depot': '2017-12-31', 'fin_achat': '31/12/18'}
        r = self.client.post(reverse('projets:projet_create'), projet_data)
        print(r.content.decode())
        self.assertEqual(r.status_code, 302)
        self.assertEqual(r.url, reverse('projets:projet', kwargs={'slug': 'first'}))
        self.assertEqual(Projet.objects.count(), 1)
        self.assertEqual(self.client.get(reverse('projets:projet_list')).status_code, 200)
        self.assertEqual(self.client.get(reverse('projets:projet', kwargs={'slug': 'first'})).status_code, 200)
