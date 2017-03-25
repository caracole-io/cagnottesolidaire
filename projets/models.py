from datetime import date

from django.contrib.auth.models import User
from django.core.urlresolvers import reverse
from django.core.validators import ValidationError
from django.db import models
from django.utils.safestring import mark_safe

from autoslug.fields import AutoSlugField


def upload_to_proj(instance, filename):
    return 'projets/proj_%s.%s' % (instance.slug, filename.split('.')[-1])


def upload_to_prop(instance, filename):
    return 'projets/proj_%s_prop_%s.%s' % (instance.projet.slug, instance.slug, filename.split('.')[-1])


def validate_positive(value):
    if value < 0:
        raise ValidationError(f'{value} n’est pas positif')


def validate_future(value):
    if value < date.today():
        raise ValidationError(f'{value} est déjà passé')


def query_sum(queryset, field='prix'):
    return queryset.aggregate(s=models.functions.Coalesce(models.Sum(field), 0))['s']


class AbstractModel(models.Model):
    nom = models.CharField(max_length=250, unique=True)
    slug = AutoSlugField(populate_from='nom', unique=True)
    created = models.DateTimeField(auto_now_add=True)
    updated = models.DateTimeField(auto_now=True)

    class Meta:
        abstract = True
        ordering = ['created']

    def __str__(self):
        return self.nom

    @property
    def absolute_url(self):
        return self.get_absolute_url()

    def link(self):
        return mark_safe(f'<a href="{self.absolute_url}">{self}</a>')


class Projet(AbstractModel):
    responsable = models.ForeignKey(User)
    image = models.ImageField('Image', upload_to=upload_to_proj, blank=True)
    objectif = models.TextField('Description de l’objectif de la cagnotte')
    finances = models.DecimalField('But à atteindre', max_digits=8, decimal_places=2, validators=[validate_positive])
    fin_depot = models.DateField('Date de fin du dépôt des propositions', validators=[validate_future],
                                 help_text='format: 31/12/2017')
    fin_achat = models.DateField('Date de fin des achats', validators=[validate_future],
                                 help_text='format: 31/12/2017')

    def get_absolute_url(self):
        return reverse('projets:projet', kwargs={'slug': self.slug})

    def offres(self):
        return Offre.objects.filter(proposition__projet=self, valide=True)

    def somme(self):
        return query_sum(self.offres())

    def somme_encaissee(self):
        return query_sum(self.offres().filter(paye=True))

    def progress(self):
        return int(round(100 * self.somme() / self.finances))

    @property
    def responsable_s(self):
        return self.responsable.get_short_name() or self.responsable.get_username()


class Proposition(AbstractModel):
    projet = models.ForeignKey(Projet)
    responsable = models.ForeignKey(User)
    description = models.TextField()
    prix = models.DecimalField(max_digits=8, decimal_places=2, validators=[validate_positive])
    beneficiaires = models.IntegerField('Nombre maximal de bénéficiaires', default=1, validators=[validate_positive],
                                        help_text='0 pour un nombre illimité')
    image = models.ImageField('Image', upload_to=upload_to_prop, blank=True)

    class Meta:
        ordering = ('projet', 'prix')

    def get_absolute_url(self):
        return reverse('projets:proposition', kwargs={'slug': self.slug, 'p_slug': self.projet.slug})

    def offres(self):
        return [self.offre_set.filter(**f).count() for f in [{}, {'valide': True}, {'paye': True}]]

    def somme(self):
        return query_sum(self.offre_set.filter(valide=True))

    @property
    def ben_s(self):
        return self.beneficiaires or '∞'

    @property
    def responsable_s(self):
        return self.responsable.get_short_name() or self.responsable.get_username()


class Offre(models.Model):
    proposition = models.ForeignKey(Proposition)
    beneficiaire = models.ForeignKey(User)
    valide = models.NullBooleanField('validé', default=None)
    paye = models.BooleanField('payé', default=False)
    remarques = models.TextField(blank=True)
    prix = models.DecimalField(max_digits=8, decimal_places=2, validators=[validate_positive])

    class Meta:
        ordering = ('paye', 'valide', 'proposition')

    def __str__(self):
        return 'offre de %s sur %s (projet %s)' % (self.beneficiaire, self.proposition, self.proposition.projet)

    def get_absolute_url(self):
        return self.proposition.absolute_url

    @property
    def responsable_s(self):
        return self.proposition.responsable.get_short_name() or self.proposition.responsable.get_username()

    @property
    def beneficiaire_s(self):
        return self.beneficiaire.get_short_name() or self.beneficiaire.get_username()
