from datetime import date
import sys

from django.contrib import messages
from django.contrib.auth.mixins import LoginRequiredMixin, UserPassesTestMixin
from django.core.mail import mail_admins
from django.shortcuts import get_object_or_404
from django.views.generic import CreateView, DetailView, ListView

from .models import Offre, Projet, Proposition


class ProjetListView(ListView):
    model = Projet


class ProjetCreateView(LoginRequiredMixin, CreateView):
    model = Projet
    fields = ['nom', 'objectif', 'finances', 'fin_depot', 'fin_achat', 'image']

    def form_valid(self, form):
        form.instance.responsable = self.request.user
        messages.success(self.request, 'Votre projet a été correctement créé !')
        return super().form_valid(form)


class ProjetDetailView(DetailView):
    model = Projet

    def get_context_data(self, **kwargs):
        return super().get_context_data(today=date.today(), **kwargs)


class PropositionCreateView(LoginRequiredMixin, CreateView):
    model = Proposition
    fields = ['nom', 'description', 'prix', 'beneficiaires', 'image']

    def form_valid(self, form):
        projet = get_object_or_404(Projet, slug=self.kwargs.get('slug', None))
        form.instance.projet = projet
        form.instance.responsable = self.request.user
        messages.success(self.request, 'Votre proposition a été correctement ajoutée !')
        return super().form_valid(form)


class PropositionDetailView(DetailView):
    model = Proposition

    def get_context_data(self, **kwargs):
        return super().get_context_data(today=date.today(), projet=self.object.projet, **kwargs)


class OffreCreateView(LoginRequiredMixin, CreateView):
    model = Offre
    fields = ['remarques']

    def get_proposition(self):
        return get_object_or_404(Proposition, slug=self.kwargs.get('slug', None))

    def form_valid(self, form):
        form.instance.proposition = self.get_proposition()
        form.instance.beneficiaire = self.request.user
        messages.success(self.request, 'Votre offre a été correctement ajoutée !')
        messages.info(self.request, 'Dès qu’elle sera validée par %s, vous recevrez un mail' %
                      form.instance.proposition.responsable)
        try:
            mail = get_template('projets/mails/offre_create.txt').render({'offre': form.instance})
            form.instance.proposition.responsable.email_user('Nouvelle offre sur votre proposition !', mail)
        except:
            mail_admins('mail d’offre pas envoyé', f'{form.instance.proposition} / {form.instance.beneficiaire}')

        return super().form_valid(form)

    def get_context_data(self, **kwargs):
        projet = get_object_or_404(Projet, slug=self.kwargs.get('p_slug', None))
        proposition = self.get_proposition()
        ct = Offre.objects.filter(proposition=proposition, beneficiaire=self.request.user).count()
        return super().get_context_data(projet=projet, proposition=proposition, count=ct, object=proposition, **kwargs)


class OffreListView(LoginRequiredMixin, ListView):
    def get_queryset(self):
        return Offre.objects.filter(beneficiaire=self.request.user)


class PropositionListView(LoginRequiredMixin, ListView):
    def get_queryset(self):
        return Proposition.objects.filter(responsable=self.request.user)


class OffreDetailView(UserPassesTestMixin, DetailView):
    model = Offre

    def test_func(self):
        if not self.request.user.is_authenticated:
            return False
        if self.request.user.is_staff:
            return True
        self.object = self.get_object()
        return self.object.proposition.responsable == self.request.user
