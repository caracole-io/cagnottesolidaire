"""Register Cagnotte Solidaire models in django admin."""
from django.contrib.admin import site

from .models import Cagnotte, Demande, Offre, Proposition

site.register(Cagnotte)
site.register(Proposition)
site.register(Offre)
site.register(Demande)
