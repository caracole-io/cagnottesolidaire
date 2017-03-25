from datetime import date

from django.contrib.auth.models import User
from django.core import mail
from django.core.urlresolvers import reverse
from django.test import TestCase

from .models import Offre, Projet, Proposition


def strpdate(s):
    d, m, y = [int(i) for i in s.split('/')]
    return date(y, m, d)


class TestProjet(TestCase):
    def setUp(self):
        for guy in 'abcs':
            User.objects.create_user(guy, email=f'{guy}@example.org', password=guy, is_staff=guy == 's')

    def test_projet(self):
        self.assertEqual(Projet.objects.count(), 0)
        self.assertEqual(self.client.get(reverse('projets:projet', kwargs={'slug': 'first'})).status_code, 404)
        self.assertEqual(self.client.get(reverse('projets:projet_list')).status_code, 200)
        self.assertEqual(self.client.get(reverse('projets:projet_create')).status_code, 302)
        self.client.login(username='a', password='a')
        self.assertEqual(self.client.get(reverse('projets:projet_create')).status_code, 200)
        projet_data = {'nom': 'first', 'objectif': 'nothing', 'finances': 42,
                       'fin_depot': '31/12/2016', 'fin_achat': '30/12/2017'}
        # fin_depot < today
        self.assertLess(strpdate(projet_data['fin_depot']), date.today())
        r = self.client.post(reverse('projets:projet_create'), projet_data)
        self.assertEqual(Projet.objects.count(), 0)
        self.assertEqual(r.status_code, 200)
        # fin_achat < fin_depot
        projet_data['fin_depot'] = '31/12/2017'
        self.assertLess(strpdate(projet_data['fin_achat']), strpdate(projet_data['fin_depot']))
        r = self.client.post(reverse('projets:projet_create'), projet_data)
        self.assertEqual(Projet.objects.count(), 0)
        self.assertEqual(r.status_code, 200)
        # OK
        projet_data['fin_achat'] = '31/12/2019'
        self.assertLess(date.today(), strpdate(projet_data['fin_depot']))
        self.assertLess(strpdate(projet_data['fin_depot']), strpdate(projet_data['fin_achat']))
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
        proposition_data = {'nom': 'Propo', 'description': 'blah blah', 'prix': '-42', 'beneficiaires': '1'}
        # prix < 0
        r = self.client.post(reverse('projets:proposition_create', kwargs=projd), proposition_data)
        self.assertEqual(Proposition.objects.count(), 0)
        self.assertEqual(r.status_code, 200)
        proposition_data['prix'] = '42'
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
        # min price is 20, so trying 18 should return an error
        r = self.client.post(reverse('projets:offre_create', kwargs=propd), {'prix': '18'})
        self.assertEqual(Offre.objects.count(), 0)
        self.assertEqual(r.status_code, 200)
        self.assertEqual(len(mail.outbox), 0)
        r = self.client.post(reverse('projets:offre_create', kwargs=propd), {'prix': '22'})
        self.assertEqual(Offre.objects.count(), 1)
        self.assertEqual(r.status_code, 302)
        self.assertEqual(len(mail.outbox), 1)
        self.assertEqual(r.url, reverse('projets:proposition', kwargs=propd))
        self.assertEqual(self.client.get(reverse('projets:proposition', kwargs=propd)).status_code, 200)
        # offre_detail
        url = reverse('projets:offre', kwargs={'pk': Offre.objects.first().pk})
        self.assertEqual(self.client.get(url).status_code, 200)
        self.client.login(username='s', password='s')
        self.assertEqual(self.client.get(url).status_code, 200)
        self.client.login(username='b', password='b')
        self.assertEqual(self.client.get(url).status_code, 302)
        self.client.logout()
        self.assertEqual(self.client.get(url).status_code, 302)

    def test_lists(self):
        self.assertEqual(self.client.get(reverse('projets:offre_list')).status_code, 302)
        self.assertEqual(self.client.get(reverse('projets:proposition_list')).status_code, 302)
        self.client.login(username='a', password='a')
        self.assertEqual(self.client.get(reverse('projets:offre_list')).status_code, 200)
        self.assertEqual(self.client.get(reverse('projets:proposition_list')).status_code, 200)
        guy = User.objects.first()
        proj = Projet.objects.create(nom='quatre', responsable=guy, objectif='nothing', finances=43,
                                     fin_depot=date(2017, 12, 31), fin_achat=date(2018, 12, 31))
        prop = Proposition.objects.create(nom='cinq', description='nope', prix=20, projet=proj, responsable=guy)
        offr = Offre.objects.create(proposition=prop, beneficiaire=guy, prix=3)
        self.assertEqual(self.client.get(reverse('projets:offre_list')).status_code, 200)
        self.assertEqual(self.client.get(reverse('projets:proposition_list')).status_code, 200)
        self.assertEqual(str(offr), 'offre de a sur cinq (projet quatre)')

    def test_fbv(self):
        a, b, c, s = User.objects.all()
        proj = Projet.objects.create(nom='fourth', responsable=a, objectif='nothing', finances=43,
                                     fin_depot=date(2017, 12, 31), fin_achat=date(2018, 12, 31))
        prop = Proposition.objects.create(nom='Pipo', description='nope', prix=20, projet=proj, responsable=b)
        offr = Offre.objects.create(proposition=prop, prix=22, beneficiaire=c)
        ok, ko, paye = [reverse(f'projets:offre_{view}', kwargs={'pk': offr.pk}) for view in ['ok', 'ko', 'paye']]

        # Must be logged in
        self.assertEqual(self.client.get(ok).url.split('?')[0], reverse('auth_login'))
        self.assertEqual(self.client.get(ko).url.split('?')[0], reverse('auth_login'))
        self.assertEqual(self.client.get(paye).url.split('?')[0], reverse('auth_login'))

        # Une offre non validée ne peut pas être payée
        self.client.login(username='a', password='a')
        self.assertEqual(self.client.get(paye).status_code, 403)

        # Seul b peut accepter ou refuser
        self.assertEqual(self.client.get(ok).status_code, 403)
        self.assertEqual(self.client.get(ko).status_code, 403)
        self.assertEqual(Offre.objects.first().valide, None)
        self.client.login(username='b', password='b')
        self.assertEqual(self.client.get(ko).status_code, 302)
        self.assertEqual(Offre.objects.first().valide, False)
        self.assertEqual(self.client.get(ok).status_code, 302)
        self.assertEqual(Offre.objects.first().valide, True)

        # Une fois que c’est accepté, seul a peut encaisser
        self.assertEqual(self.client.get(paye).status_code, 403)
        self.assertEqual(Offre.objects.first().paye, False)
        self.client.login(username='a', password='a')
        self.assertEqual(self.client.get(paye).status_code, 302)
        self.assertEqual(Offre.objects.first().paye, True)
