from datetime import date

from django.contrib.auth.models import User
from django.core.urlresolvers import reverse
from django.test import TestCase

from .models import Offre, Projet, Proposition


class TestProjet(TestCase):
    def setUp(self):
        guy = 'a'
        User.objects.create_user(guy, email=f'{guy}@example.org', password=guy)

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
        self.assertEqual(Projet.objects.count(), 1)
        self.assertEqual(r.status_code, 302)
        self.assertEqual(r.url, reverse('projets:projet', kwargs={'slug': 'first'}))
        self.assertEqual(self.client.get(reverse('projets:projet_list')).status_code, 200)
        self.assertEqual(self.client.get(reverse('projets:projet', kwargs={'slug': 'first'})).status_code, 200)

    def test_proposition(self):
        guy = User.objects.first()
        self.assertEqual(Proposition.objects.count(), 0)
        self.assertEqual(Projet.objects.count(), 0)
        proj = Projet.objects.create(nom='second', responsable=guy, objectif='nothing', finances=43,
                                     fin_depot=date(2017, 12, 31), fin_achat=date(2018, 12, 31))
        projd = {'slug': proj.slug}
        propd = {'p_slug': proj.slug, 'slug': 'propo'}
        self.assertEqual(self.client.get(reverse('projets:proposition', kwargs=propd)).status_code, 404)
        self.assertEqual(self.client.get(reverse('projets:projet', kwargs=projd)).status_code, 200)
        self.assertEqual(self.client.get(reverse('projets:proposition_create', kwargs=projd)).status_code, 302)
        self.client.login(username='a', password='a')
        self.assertEqual(self.client.get(reverse('projets:proposition_create', kwargs=projd)).status_code, 200)
        proposition_data = {'nom': 'Propo', 'description': 'blah blah', 'prix': '42', 'beneficiaires': '1'}
        r = self.client.post(reverse('projets:proposition_create', kwargs=projd), proposition_data)
        self.assertEqual(Proposition.objects.count(), 1)
        self.assertEqual(r.status_code, 302)
        self.assertEqual(r.url, reverse('projets:proposition', kwargs=propd))
        self.assertEqual(self.client.get(reverse('projets:projet', kwargs=projd)).status_code, 200)
        self.assertEqual(self.client.get(reverse('projets:proposition', kwargs=propd)).status_code, 200)

    def test_offre(self):
        guy = User.objects.first()
        proj = Projet.objects.create(nom='third', responsable=guy, objectif='nothing', finances=43,
                                     fin_depot=date(2017, 12, 31), fin_achat=date(2018, 12, 31))
        prop = Proposition.objects.create(nom='Pipo', description='nope', prix=20, projet=proj, responsable=guy)
        propd = {'p_slug': proj.slug, 'slug': prop.slug}
        self.assertEqual(self.client.get(reverse('projets:proposition', kwargs=propd)).status_code, 200)
        self.assertEqual(Offre.objects.count(), 0)
        self.assertEqual(self.client.get(reverse('projets:offre_create', kwargs=propd)).status_code, 302)
        self.client.login(username='a', password='a')
        self.assertEqual(self.client.get(reverse('projets:offre_create', kwargs=propd)).status_code, 200)
        r = self.client.post(reverse('projets:offre_create', kwargs=propd))
        self.assertEqual(Offre.objects.count(), 1)
        self.assertEqual(r.status_code, 302)
        self.assertEqual(r.url, reverse('projets:proposition', kwargs=propd))
        self.assertEqual(self.client.get(reverse('projets:proposition', kwargs=propd)).status_code, 200)
