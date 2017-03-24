from django.forms import ModelForm

from .models import Offre, Projet


class ProjetForm(ModelForm):
    class Meta:
        model = Projet
        fields = ['nom', 'objectif', 'finances', 'fin_depot', 'fin_achat', 'image']

    def clean(self):
        cleaned_data = super().clean()
        fin_depot = cleaned_data.get('fin_depot')
        fin_achat = cleaned_data.get('fin_achat')

        if fin_achat < fin_depot:
            msg = 'La fin du dépôt des propositions doit être antérieure à la fin des achats'
            self.add_error('fin_depot', msg)
            self.add_error('fin_achat', msg)


class OffreForm(ModelForm):
    class Meta:
        model = Offre
        fields = ['prix', 'remarques']

    def clean(self):
        prix_user = super().clean().get('prix')
        prix_prop = self.initial['proposition'].prix
        if prix_user < prix_prop:
            self.add_error('prix', f'Votre prix ({prix_user}) ne peut pas être inférieur à la demande ({prix_prop})')
