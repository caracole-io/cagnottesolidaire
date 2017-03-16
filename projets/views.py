from django.contrib.auth.mixins import LoginRequiredMixin
from django.views.generic import ListView, CreateView, DetailView

from .models import Projet


class ProjetListView(ListView):
    model = Projet


class ProjetCreateView(LoginRequiredMixin, CreateView):
    model = Projet
    fields = ['nom', 'objectif', 'finances', 'fin_depot', 'fin_achat', 'pict', 'jumbo']

    def form_valid(self, form):
        form.instance.responsable = self.request.user
        super().form_valid(form)


class ProjetDetailView(DetailView):
    model = Projet
