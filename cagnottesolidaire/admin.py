from django.contrib.admin import site

from .models import Offre, Cagnotte, Proposition

site.register(Cagnotte)
site.register(Proposition)
site.register(Offre)
