from datetime import date

from django.conf import settings
from django.contrib import messages
from django.contrib.auth.mixins import LoginRequiredMixin, UserPassesTestMixin
from django.contrib.auth.decorators import login_required
from django.core.exceptions import PermissionDenied
from django.core.mail import mail_admins
from django.shortcuts import get_object_or_404, redirect
from django.template.loader import get_template
from django.views.generic import CreateView, DetailView, ListView

from .forms import OffreForm, ProjetForm
from .models import Offre, Projet, Proposition


class ProjetListView(ListView):
    model = Projet


class ProjetCreateView(LoginRequiredMixin, CreateView):
    model = Projet
    form_class = ProjetForm

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
    form_class = OffreForm

    def get_proposition(self):
        return get_object_or_404(Proposition, slug=self.kwargs.get('slug', None))

    def form_valid(self, form):
        proposition = self.get_proposition()
        if not proposition.offrable():
            raise PermissionDenied
        form.instance.proposition = proposition
        form.instance.beneficiaire = self.request.user
        messages.success(self.request, 'Votre offre a été correctement ajoutée !')
        messages.info(self.request, f'Dès qu’elle sera validée par {proposition.responsable_s}, vous recevrez un mail')
        if not settings.DEBUG:
            try:
                mail = get_template('cagnottesolidaire/mails/offre_create.txt').render({'offre': form.instance})
                proposition.responsable.email_user('Nouvelle offre sur votre proposition !', mail)
            except Exception as e:  # pragma: no cover
                mail_admins('mail d’offre pas envoyé', f'{form.instance.pk} / {proposition.responsable}:\n{e!r}')
        return super().form_valid(form)

    def get_context_data(self, **kwargs):
        projet = get_object_or_404(Projet, slug=self.kwargs.get('p_slug', None))
        proposition = self.get_proposition()
        ct = Offre.objects.filter(proposition=proposition, beneficiaire=self.request.user).count()
        return super().get_context_data(projet=projet, proposition=proposition, count=ct, object=proposition, **kwargs)

    def get_initial(self):
        prop = self.get_proposition()
        return {'prix': prop.prix, 'proposition': prop}


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


@login_required
def offre_ok(request, pk):
    offre = get_object_or_404(Offre, pk=pk)
    if offre.proposition.responsable != request.user:
        raise PermissionDenied
    offre.valide = True
    offre.save()
    messages.success(request, f'Vous avez accepté l’offre de {offre.beneficiaire_s}, un mail lui a été envoyé')
    try:
        mail = get_template('cagnottesolidaire/mails/offre_ok.txt').render({'offre': offre})
        offre.beneficiaire.email_user('Votre offre a été acceptée !', mail)
    except Exception as e:  # pragma: no cover
        mail_admins('mail d’offre OK pas envoyé', f'{offre.pk} / {offre.beneficiaire_s}:\n{e!r}')
    return redirect(offre)


@login_required
def offre_ko(request, pk):
    offre = get_object_or_404(Offre, pk=pk)
    if offre.proposition.responsable != request.user:
        raise PermissionDenied
    offre.valide = False
    offre.save()
    messages.warning(request, f'Vous avez refusé l’offre de {offre.beneficiaire_s}, un mail lui a été envoyé')
    try:
        mail = get_template('cagnottesolidaire/mails/offre_ko.txt').render({'offre': offre})
        offre.beneficiaire.email_user('Votre offre a été refusée', mail)
    except Exception as e:  # pragma: no cover
        mail_admins('mail d’offre KO pas envoyé', f'{offre.pk} / {offre.beneficiaire_s}:\n{e!r}')
    return redirect(offre)


@login_required
def offre_paye(request, pk):
    offre = get_object_or_404(Offre, pk=pk)
    if offre.proposition.projet.responsable != request.user or not offre.valide:
        raise PermissionDenied
    offre.paye = True
    offre.save()
    messages.success(request, f'L’offre {offre.pk} a bien été marquée comme payée !')
    return redirect(offre.proposition.projet)
