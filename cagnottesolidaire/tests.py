from datetime import date

from django.contrib.auth.models import User
from django.core import mail
from django.urls import reverse
from django.test import TestCase

from .models import Cagnotte, Demande, Offre, Proposition


def strpdate(s):
    d, m, y = [int(i) for i in s.split('/')]
    return date(y, m, d)


class TestCagnotte(TestCase):
    def setUp(self):
        for guy in 'abcs':
            User.objects.create_user(guy, email=f'{guy}@example.org', password=guy, is_staff=guy == 's')

    def test_cagnotte(self):
        self.assertEqual(Cagnotte.objects.count(), 0)
        self.assertEqual(self.client.get(reverse('cagnottesolidaire:cagnotte', kwargs={'slug': 'first'})).status_code,
                         404)
        self.assertEqual(self.client.get(reverse('cagnottesolidaire:cagnotte_list')).status_code, 200)
        self.assertEqual(self.client.get(reverse('cagnottesolidaire:cagnotte_create')).status_code, 302)
        self.client.login(username='a', password='a')
        self.assertEqual(self.client.get(reverse('cagnottesolidaire:cagnotte_create')).status_code, 200)
        cagnotte_data = {'name': 'first', 'objectif': 'nothing', 'finances': 42,
                         'fin_depot': '31/12/2016', 'fin_achat': '30/12/2017'}
        # fin_depot < today
        self.assertLess(strpdate(cagnotte_data['fin_depot']), date.today())
        r = self.client.post(reverse('cagnottesolidaire:cagnotte_create'), cagnotte_data)
        self.assertEqual(Cagnotte.objects.count(), 0)
        self.assertEqual(r.status_code, 200)
        # fin_achat < fin_depot
        cagnotte_data['fin_depot'] = '31/12/2018'
        self.assertLess(strpdate(cagnotte_data['fin_achat']), strpdate(cagnotte_data['fin_depot']))
        r = self.client.post(reverse('cagnottesolidaire:cagnotte_create'), cagnotte_data)
        self.assertEqual(Cagnotte.objects.count(), 0)
        self.assertEqual(r.status_code, 200)
        # OK
        cagnotte_data['fin_achat'] = '31/12/2020'
        self.assertLess(date.today(), strpdate(cagnotte_data['fin_depot']))
        self.assertLess(strpdate(cagnotte_data['fin_depot']), strpdate(cagnotte_data['fin_achat']))
        r = self.client.post(reverse('cagnottesolidaire:cagnotte_create'), cagnotte_data)
        self.assertEqual(Cagnotte.objects.count(), 1)
        self.assertEqual(r.status_code, 302)
        self.assertEqual(r.url, reverse('cagnottesolidaire:cagnotte', kwargs={'slug': 'first'}))
        self.assertEqual(self.client.get(reverse('cagnottesolidaire:cagnotte_list')).status_code, 200)
        self.assertEqual(self.client.get(reverse('cagnottesolidaire:cagnotte', kwargs={'slug': 'first'})).status_code,
                         200)

    def test_proposition(self):
        guy = User.objects.first()
        self.assertEqual(Proposition.objects.count(), 0)
        self.assertEqual(Cagnotte.objects.count(), 0)
        proj = Cagnotte.objects.create(name='second', responsable=guy, objectif='nothing', finances=43,
                                       fin_depot=date(2017, 12, 31), fin_achat=date(2018, 12, 31))
        projd = {'slug': proj.slug}
        propd = {'p_slug': proj.slug, 'slug': 'propo'}
        self.assertEqual(self.client.get(reverse('cagnottesolidaire:proposition', kwargs=propd)).status_code, 404)
        self.assertEqual(self.client.get(reverse('cagnottesolidaire:cagnotte', kwargs=projd)).status_code, 200)
        self.assertEqual(self.client.get(reverse('cagnottesolidaire:proposition_create', kwargs=projd)).status_code,
                         302)
        self.client.login(username='a', password='a')
        self.assertEqual(self.client.get(reverse('cagnottesolidaire:proposition_create', kwargs=projd)).status_code,
                         200)
        proposition_data = {'name': 'Propo', 'description': 'blah blah', 'prix': '-42', 'beneficiaires': '1'}
        # prix < 0
        r = self.client.post(reverse('cagnottesolidaire:proposition_create', kwargs=projd), proposition_data)
        self.assertEqual(Proposition.objects.count(), 0)
        self.assertEqual(r.status_code, 200)
        proposition_data['prix'] = '42'
        r = self.client.post(reverse('cagnottesolidaire:proposition_create', kwargs=projd), proposition_data)
        self.assertEqual(Proposition.objects.count(), 1)
        self.assertEqual(r.status_code, 302)
        self.assertEqual(r.url, reverse('cagnottesolidaire:proposition', kwargs=propd))
        self.assertEqual(self.client.get(reverse('cagnottesolidaire:cagnotte', kwargs=projd)).status_code, 200)
        self.assertEqual(self.client.get(reverse('cagnottesolidaire:proposition', kwargs=propd)).status_code, 200)

    def test_offre(self):
        guy = User.objects.first()
        proj = Cagnotte.objects.create(name='third', responsable=guy, objectif='nothing', finances=43,
                                       fin_depot=date(2017, 12, 31), fin_achat=date(2018, 12, 31))
        prop = Proposition.objects.create(name='Pipo', description='nope', prix=20, cagnotte=proj, responsable=guy)
        propd = {'p_slug': proj.slug, 'slug': prop.slug}
        self.assertEqual(self.client.get(reverse('cagnottesolidaire:proposition', kwargs=propd)).status_code, 200)
        self.assertEqual(Offre.objects.count(), 0)
        self.assertEqual(self.client.get(reverse('cagnottesolidaire:offre_create', kwargs=propd)).status_code, 302)
        self.client.login(username='a', password='a')
        self.assertEqual(self.client.get(reverse('cagnottesolidaire:offre_create', kwargs=propd)).status_code, 200)
        # min price is 20, so trying 18 should return an error
        r = self.client.post(reverse('cagnottesolidaire:offre_create', kwargs=propd), {'prix': '18'})
        self.assertEqual(Offre.objects.count(), 0)
        self.assertEqual(r.status_code, 200)
        self.assertEqual(len(mail.outbox), 0)
        r = self.client.post(reverse('cagnottesolidaire:offre_create', kwargs=propd), {'prix': '22'})
        self.assertEqual(Offre.objects.count(), 1)
        self.assertEqual(r.status_code, 302)
        self.assertEqual(len(mail.outbox), 1)
        self.assertEqual(r.url, reverse('cagnottesolidaire:proposition', kwargs=propd))
        self.assertEqual(self.client.get(reverse('cagnottesolidaire:proposition', kwargs=propd)).status_code, 200)
        # offre_detail
        url = reverse('cagnottesolidaire:offre', kwargs={'pk': Offre.objects.first().pk})
        self.assertEqual(self.client.get(url).status_code, 200)
        self.client.login(username='s', password='s')
        self.assertEqual(self.client.get(url).status_code, 200)
        self.client.login(username='b', password='b')
        self.assertEqual(self.client.get(url).status_code, 302)
        self.client.logout()
        self.assertEqual(self.client.get(url).status_code, 302)

    def test_lists(self):
        self.assertEqual(self.client.get(reverse('cagnottesolidaire:offre_list')).status_code, 302)
        self.assertEqual(self.client.get(reverse('cagnottesolidaire:proposition_list')).status_code, 302)
        self.client.login(username='a', password='a')
        self.assertEqual(self.client.get(reverse('cagnottesolidaire:offre_list')).status_code, 200)
        self.assertEqual(self.client.get(reverse('cagnottesolidaire:proposition_list')).status_code, 200)
        guy = User.objects.first()
        proj = Cagnotte.objects.create(name='quatre', responsable=guy, objectif='nothing', finances=43,
                                       fin_depot=date(2017, 12, 31), fin_achat=date(2018, 12, 31))
        prop = Proposition.objects.create(name='cinq', description='nope', prix=20, cagnotte=proj, responsable=guy)
        offr = Offre.objects.create(proposition=prop, beneficiaire=guy, prix=3)
        self.assertEqual(self.client.get(reverse('cagnottesolidaire:offre_list')).status_code, 200)
        self.assertEqual(self.client.get(reverse('cagnottesolidaire:proposition_list')).status_code, 200)
        self.assertEqual(str(offr), 'offre de a sur cinq (cagnotte quatre)')

    def test_fbv(self):
        a, b, c, s = User.objects.all()
        proj = Cagnotte.objects.create(name='fourth', responsable=a, objectif='nothing', finances=43,
                                       fin_depot=date(2017, 12, 31), fin_achat=date(2018, 12, 31))
        prop = Proposition.objects.create(name='Pipo', description='nope', prix=20, cagnotte=proj, responsable=b)
        offr = Offre.objects.create(proposition=prop, prix=22, beneficiaire=c)
        ok, ko, paye = [reverse(f'cagnottesolidaire:offre_{view}', kwargs={'pk': offr.pk})
                        for view in ['ok', 'ko', 'paye']]

        # Must be logged in
        self.assertEqual(self.client.get(ok).url.split('?')[0], reverse('login'))
        self.assertEqual(self.client.get(ko).url.split('?')[0], reverse('login'))
        self.assertEqual(self.client.get(paye).url.split('?')[0], reverse('login'))

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

    def test_offrable(self):
        a, b, c, s = User.objects.all()
        proj = Cagnotte.objects.create(name='fifth', responsable=a, objectif='nothing', finances=43,
                                       fin_depot=date(2017, 12, 31), fin_achat=date(2018, 12, 31))
        prop = Proposition.objects.create(name='Pipo', description='nope', prix=20, cagnotte=proj, responsable=b,
                                          beneficiaires=2)
        self.client.login(username='c', password='c')
        self.assertEqual(Offre.objects.count(), 0)
        url = reverse('cagnottesolidaire:offre_create', kwargs={'p_slug': proj.slug, 'slug': prop.slug})
        self.assertEqual(self.client.post(url, {'prix': '21'}).status_code, 302)
        self.assertEqual(Offre.objects.count(), 1)
        self.assertEqual(self.client.post(url, {'prix': '21'}).status_code, 302)
        self.assertEqual(Offre.objects.count(), 2)
        self.assertEqual(self.client.post(url, {'prix': '21'}).status_code, 302)
        self.assertEqual(Offre.objects.count(), 3)

        # old
        proj = Cagnotte.objects.create(name='sixth', responsable=a, objectif='nothing', finances=43,
                                       fin_depot=date(2014, 12, 31), fin_achat=date(2015, 12, 31))
        prop = Proposition.objects.create(name='popo', description='nope', prix=20, cagnotte=proj, responsable=b,
                                          beneficiaires=2)
        self.client.login(username='c', password='c')
        self.assertEqual(Offre.objects.count(), 3)
        url = reverse('cagnottesolidaire:offre_create', kwargs={'p_slug': proj.slug, 'slug': prop.slug})
        self.assertEqual(self.client.post(url, {'prix': '21'}).status_code, 403)
        self.assertEqual(Offre.objects.count(), 3)

    def test_demande(self):
        guy = User.objects.first()
        self.assertEqual(Demande.objects.count(), 0)
        proj = Cagnotte.objects.create(name='last', responsable=guy, objectif='nothing', finances=43,
                                       fin_depot=date(2017, 12, 31), fin_achat=date(2018, 12, 31))
        data = {'slug': proj.slug}
        # Not logged in
        self.assertEqual(self.client.get(reverse('cagnottesolidaire:demande_create', kwargs=data)).status_code, 302)
        self.client.login(username='c', password='c')
        self.assertEqual(self.client.get(reverse('cagnottesolidaire:demande_create', kwargs=data)).status_code, 200)
        demande_data = {'description': 'cours de massage'}
        r = self.client.post(reverse('cagnottesolidaire:demande_create', kwargs=data), demande_data)
        self.assertEqual(Demande.objects.count(), 1)
        self.assertEqual(r.status_code, 302)
        self.assertEqual(self.client.get(reverse('cagnottesolidaire:cagnotte', kwargs=data)).status_code, 200)

        delete_url = reverse('cagnottesolidaire:demande_delete', kwargs={'pk': Demande.objects.first().pk})
        self.assertEqual(self.client.get(delete_url).status_code, 200)
        self.client.post(delete_url)
        self.assertEqual(Demande.objects.count(), 0)
