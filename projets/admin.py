from django.contrib.admin import site

from .models import Projet, Proposition, Offre


site.register(Projet)
site.register(Proposition)
site.register(Offre)
