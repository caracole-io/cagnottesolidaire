from datetime import date

from django.contrib.auth.models import User
from django.urls import reverse
from django.core.validators import ValidationError
from django.db import models
from django.utils.safestring import mark_safe

from ndh.models import Links, TimeStampedModel, NamedModel
from ndh.utils import query_sum


def upload_to_proj(instance, filename):
    return f'cagnottesolidaire/proj_{instance.slug}.' + filename.split('.')[-1]


def upload_to_prop(instance, filename):
    return f'cagnottesolidaire/proj_{instance.cagnotte.slug}_prop_{instance.slug}.' + filename.split('.')[-1]


def validate_positive(value):
    if value < 0:
        raise ValidationError(f'{value} n’est pas positif')


def validate_future(value):
    if value < date.today():
        raise ValidationError(f'{value} est déjà passé')


class Cagnotte(Links, TimeStampedModel, NamedModel):
    responsable = models.ForeignKey(User, on_delete=models.PROTECT)
    image = models.ImageField('Image', upload_to=upload_to_proj, blank=True)
    objectif = models.TextField('Description de l’objectif de la cagnotte')
    finances = models.DecimalField('But à atteindre', max_digits=8, decimal_places=2, validators=[validate_positive])
    fin_depot = models.DateField('Date de fin du dépôt des propositions', validators=[validate_future])
    fin_achat = models.DateField('Date de fin des achats', validators=[validate_future])

    def offres(self):
        return Offre.objects.filter(proposition__cagnotte=self, valide=True)

    def somme(self):
        return query_sum(self.offres(), 'prix')

    def somme_encaissee(self):
        return query_sum(self.offres().filter(paye=True), 'prix')

    def progress(self):
        return int(round(100 * self.somme() / self.finances))

    @property
    def responsable_s(self):
        return self.responsable.get_short_name() or self.responsable.get_username()


class Proposition(Links, TimeStampedModel, NamedModel):
    cagnotte = models.ForeignKey(Cagnotte, on_delete=models.PROTECT)
    responsable = models.ForeignKey(User, on_delete=models.PROTECT)
    description = models.TextField()
    prix = models.DecimalField(max_digits=8, decimal_places=2, validators=[validate_positive])
    beneficiaires = models.IntegerField('Nombre maximal de bénéficiaires', default=1, validators=[validate_positive],
                                        help_text='0 pour un nombre illimité')
    image = models.ImageField('Image', upload_to=upload_to_prop, blank=True)

    class Meta:
        ordering = ('cagnotte', 'prix')

    def get_absolute_url(self):
        return reverse('cagnottesolidaire:proposition', kwargs={'slug': self.slug, 'p_slug': self.cagnotte.slug})

    def offres(self):
        return [self.offre_set.filter(**f).count() for f in [{}, {'valide': True}, {'paye': True}]]

    def offrable(self):
        if date.today() > self.cagnotte.fin_achat:
            return False
        return self.beneficiaires == 0 or self.offre_set.filter(valide=True).count() < self.beneficiaires

    def somme(self):
        return query_sum(self.offre_set.filter(valide=True), 'prix')

    @property
    def ben_s(self):
        return self.beneficiaires or '∞'

    @property
    def responsable_s(self):
        return self.responsable.get_short_name() or self.responsable.get_username()


class Offre(Links, models.Model):
    proposition = models.ForeignKey(Proposition, on_delete=models.PROTECT)
    beneficiaire = models.ForeignKey(User, on_delete=models.PROTECT)
    valide = models.NullBooleanField('validé', default=None)
    paye = models.BooleanField('payé', default=False)
    remarques = models.TextField(blank=True)
    prix = models.DecimalField(max_digits=8, decimal_places=2, validators=[validate_positive])

    class Meta:
        ordering = ('paye', 'valide', 'proposition')

    def __str__(self):
        return f'offre de {self.beneficiaire} sur {self.proposition} (cagnotte {self.proposition.cagnotte})'

    def get_absolute_url(self):
        return self.proposition.get_absolute_url()

    @property
    def responsable_s(self):
        return self.proposition.responsable.get_short_name() or self.proposition.responsable.get_username()

    @property
    def beneficiaire_s(self):
        return self.beneficiaire.get_short_name() or self.beneficiaire.get_username()


class Demande(models.Model):
    cagnotte = models.ForeignKey(Cagnotte, on_delete=models.PROTECT)
    demandeur = models.ForeignKey(User, on_delete=models.PROTECT)
    description = models.CharField(max_length=250)

    def __str__(self):
        return self.description

    def get_absolute_url(self):
        return self.cagnotte.get_absolute_url()
