from django.db import models
from django.contrib.auth.models import User

from autoslug.fields import AutoSlugField


def upload_to_jumbo(instance, filename):
    return 'projets/%s_jumbo.%s' % (instance.slug, filename.split('.')[-1])


def upload_to_pict(instance, filename):
    return 'projets/%s_pict.%s' % (instance.slug, filename.split('.')[-1])


def upload_to_prop(instance, filename):
    return 'projets/%s_prop_%s.%s' % (instance.projet.slug, instance.slug, filename.split('.')[-1])


class AbstractModel(models.Model):
    nom = models.CharField(max_length=250, unique=True)
    slug = AutoSlugField(populate_from='nom', unique=True)
    created = models.DateTimeField(auto_now_add=True)
    updated = models.DateTimeField(auto_now=True)

    class Meta:
        abtract = True
        order_by = 'created'

    def __str__(self):
        return self.nom


class Projet(AbstractModel):
    responsable = models.ForeignKey(User)
    jumbo = models.ImageField('Grande image', upload_to=upload_to_jumbo, blank=True)
    pict = models.ImageField('Petite image', upload_to=upload_to_pict, blank=True)
    objectif = models.TextField('Description de l’objectif de la cagnotte')
    finances = models.DecimalField('But à atteindre', max_digits=8, decimal_places=2)
    fin_depot = models.DateField('Fin du dépôt des propositions')
    fin_achat = models.DateField('Fin des achats')


class Proposition(AbstractModel):
    projet = models.ForeignKey(Projet)
    responsable = models.ForeignKey(User)
    description = models.TextField()
    prix = models.DecimalField(max_digits=8, decimal_places=2)
    beneficiaires = models.IntegerField('Nombre maximal de bénéficiaires', default=1)
    image = models.ImageField('Image', upload_to=upload_to_prop, blank=True)


class Offre(models.Model):
    proposition = models.ForeignKey(Proposition)
    beneficiaire = models.ForeignKey(User)
    valide = models.NullBooleanField('validé', default=None)
    paye = models.BooleanField('payé', default=False)

    def __str__(self):
        return 'offre de %s sur %s (projet %s)' % (self.beneficiaire, self.proposition, self.proposition.projet)
