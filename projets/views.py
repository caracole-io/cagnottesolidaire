from datetime import date
from django.contrib.auth.mixins import LoginRequiredMixin
from django.views.generic import ListView, CreateView, DetailView
from django.contrib import messages

from .models import Projet


class ProjetListView(ListView):
    model = Projet


class ProjetCreateView(LoginRequiredMixin, CreateView):
    model = Projet
    fields = ['nom', 'objectif', 'finances', 'fin_depot', 'fin_achat', 'pict', 'jumbo']

    def form_valid(self, form):
        form.instance.responsable = self.request.user
        messages.success(self.request, 'Votre projet a été correctement créé !')
        return super().form_valid(form)


class ProjetDetailView(DetailView):
    model = Projet

    def get_context_data(self, **kwargs):
        return super().get_context_data(today=date.today(), **kwargs)
