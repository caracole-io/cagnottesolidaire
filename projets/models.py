from django.contrib.auth.models import User
from django.core.urlresolvers import reverse
from django.db import models
from django.utils.safestring import mark_safe

from autoslug.fields import AutoSlugField


def upload_to_proj(instance, filename):
    return 'projets/proj_%s.%s' % (instance.slug, filename.split('.')[-1])


def upload_to_prop(instance, filename):
    return 'projets/proj_%s_prop_%s.%s' % (instance.projet.slug, instance.slug, filename.split('.')[-1])


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
    finances = models.DecimalField('But à atteindre', max_digits=8, decimal_places=2)  # TODO > 0
    fin_depot = models.DateField('Date de fin du dépôt des propositions',
                                 help_text='format: 31/12/2017')  # TODO > today
    fin_achat = models.DateField('Date de fin des achats',
                                 help_text='format: 31/12/2017')  # TODO > depot

    def get_absolute_url(self):
        return reverse('projets:projet', kwargs={'slug': self.slug})


class Proposition(AbstractModel):
    projet = models.ForeignKey(Projet)
    responsable = models.ForeignKey(User)
    description = models.TextField()
    prix = models.DecimalField(max_digits=8, decimal_places=2)  # TODO > 0
    beneficiaires = models.IntegerField('Nombre maximal de bénéficiaires', default=1,
                                        help_text='0 pour un nombre illimité')  # TODO >= 0
    image = models.ImageField('Image', upload_to=upload_to_prop, blank=True)

    class Meta:
        ordering = ('projet', 'prix')

    def get_absolute_url(self):
        return reverse('projets:proposition', kwargs={'slug': self.slug, 'p_slug': self.projet.slug})

    def offres(self):
        return [self.offre_set.filter(**f).count() for f in [{}, {'valide': True}, {'paye': True}]]


class Offre(models.Model):
    proposition = models.ForeignKey(Proposition)
    beneficiaire = models.ForeignKey(User)
    valide = models.NullBooleanField('validé', default=None)
    paye = models.BooleanField('payé', default=False)

    class Meta:
        ordering = ('paye', 'valide', 'proposition')

    def __str__(self):
        return 'offre de %s sur %s (projet %s)' % (self.beneficiaire, self.proposition, self.proposition.projet)

    def get_absolute_url(self):
        return self.proposition.absolute_url
