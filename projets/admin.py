from django.contrib.admin import site

from .models import Offre, Projet, Proposition

site.register(Projet)
site.register(Proposition)
site.register(Offre)
