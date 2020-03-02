"""Forms for the Cagnotte Solidaire Django application."""
from django import forms

from .models import Cagnotte, Offre


class CagnotteForm(forms.ModelForm):
    """ModelForm for the Cagnotte model."""
    class Meta:
        """Meta."""
        model = Cagnotte
        fields = ['name', 'objectif', 'finances', 'fin_depot', 'fin_achat', 'image']
        widgets = {'fin_depot': forms.SelectDateWidget, 'fin_achat': forms.SelectDateWidget}

    def clean(self):
        """Check dates."""
        cleaned_data = super().clean()
        fin_depot = cleaned_data.get('fin_depot')
        fin_achat = cleaned_data.get('fin_achat')

        if fin_achat is not None and fin_depot is not None and fin_achat < fin_depot:
            msg = 'La fin du dépôt des propositions doit être antérieure à la fin des achats'
            self.add_error('fin_depot', msg)
            self.add_error('fin_achat', msg)


class OffreForm(forms.ModelForm):
    """ModelForm for the Offre model."""
    class Meta:
        """Meta."""
        model = Offre
        fields = ['prix', 'remarques']

    def clean(self):
        """Check the price of this Offre."""
        prix_user = super().clean().get('prix')
        prix_prop = self.initial['proposition'].prix
        if prix_user < prix_prop:
            self.add_error('prix', f'Votre prix ({prix_user}) ne peut pas être inférieur à la demande ({prix_prop})')
