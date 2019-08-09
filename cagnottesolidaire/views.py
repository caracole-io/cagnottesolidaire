from datetime import date

from django.conf import settings
from django.contrib import messages
from django.contrib.auth.decorators import login_required
from django.contrib.auth.mixins import LoginRequiredMixin
from django.core.exceptions import PermissionDenied
from django.core.mail import mail_admins
from django.shortcuts import get_object_or_404, redirect
from django.template.loader import get_template
from django.views.generic import CreateView, DeleteView, DetailView, ListView

from .forms import CagnotteForm, OffreForm
from .models import Cagnotte, Demande, Offre, Proposition
from .utils import IsUserOrAboveMixin


class CagnotteListView(ListView):
    model = Cagnotte


class CagnotteCreateView(LoginRequiredMixin, CreateView):
    model = Cagnotte
    form_class = CagnotteForm

    def form_valid(self, form):
        form.instance.responsable = self.request.user
        messages.success(self.request, 'Votre cagnotte a été correctement créée !')
        return super().form_valid(form)


class CagnotteDetailView(DetailView):
    model = Cagnotte

    def get_context_data(self, **kwargs):
        return super().get_context_data(today=date.today(), **kwargs)


class PropositionCreateView(LoginRequiredMixin, CreateView):
    model = Proposition
    fields = ['name', 'description', 'prix', 'beneficiaires', 'image']

    def form_valid(self, form):
        cagnotte = get_object_or_404(Cagnotte, slug=self.kwargs.get('slug', None))
        form.instance.cagnotte = cagnotte
        form.instance.responsable = self.request.user
        messages.success(self.request, 'Votre proposition a été correctement ajoutée !')
        return super().form_valid(form)


class PropositionDetailView(DetailView):
    model = Proposition

    def get_context_data(self, **kwargs):
        return super().get_context_data(today=date.today(), cagnotte=self.object.cagnotte, **kwargs)


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
                template = 'cagnottesolidaire/mails/offre_create.%s'
                mail, html = (get_template(template % alt).render({'offre': form.instance}) for alt in ['txt', 'html'])

                proposition.responsable.email_user('Nouvelle offre sur votre proposition !', mail, html_message=html)
            except Exception as e:
                mail_admins('mail d’offre pas envoyé', f'{form.instance.pk} / {proposition.responsable}:\n{e!r}')
        return super().form_valid(form)

    def get_context_data(self, **kwargs):
        cagnotte = get_object_or_404(Cagnotte, slug=self.kwargs.get('p_slug', None))
        proposition = self.get_proposition()
        count = Offre.objects.filter(proposition=proposition, beneficiaire=self.request.user).count()
        return super().get_context_data(cagnotte=cagnotte,
                                        proposition=proposition,
                                        count=count,
                                        object=proposition,
                                        **kwargs)

    def get_initial(self):
        prop = self.get_proposition()
        return {'prix': prop.prix, 'proposition': prop}


class OffreListView(LoginRequiredMixin, ListView):
    def get_queryset(self):
        return Offre.objects.filter(beneficiaire=self.request.user)


class PropositionListView(LoginRequiredMixin, ListView):
    def get_queryset(self):
        return Proposition.objects.filter(responsable=self.request.user)


class OffreDetailView(IsUserOrAboveMixin, DetailView):
    model = Offre

    def get_user(self):
        return self.get_object().proposition.responsable


class DemandeCreateView(LoginRequiredMixin, CreateView):
    model = Demande
    fields = ('description', )

    def form_valid(self, form):
        form.instance.demandeur = self.request.user
        form.instance.cagnotte = get_object_or_404(Cagnotte, slug=self.kwargs['slug'])
        messages.success(self.request, 'Votre demande a été correctement enregistrée !')
        return super().form_valid(form)


class DemandeDeleteView(IsUserOrAboveMixin, DeleteView):
    model = Demande

    def get_success_url(self):
        return self.object.get_absolute_url()

    def get_user(self):
        return self.get_object().demandeur


@login_required
def offre_ok(request, pk):
    offre = get_object_or_404(Offre, pk=pk)
    if offre.proposition.responsable != request.user:
        raise PermissionDenied
    offre.valide = True
    offre.save()
    messages.success(request, f'Vous avez accepté l’offre de {offre.beneficiaire_s}, un mail lui a été envoyé')
    try:
        template = 'cagnottesolidaire/mails/offre_ok.%s'
        mail, html = (get_template(template % alt).render({'offre': offre}) for alt in ['txt', 'html'])
        offre.beneficiaire.email_user('Votre offre a été acceptée !', mail, html_message=html)
    except Exception as e:
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
        template = 'cagnottesolidaire/mails/offre_ko.%s'
        mail, html = (get_template(template % alt).render({'offre': offre}) for alt in ['txt', 'html'])
        offre.beneficiaire.email_user('Votre offre a été refusée', mail, html_message=html)
    except Exception as e:
        mail_admins('mail d’offre KO pas envoyé', f'{offre.pk} / {offre.beneficiaire_s}:\n{e!r}')
    return redirect(offre)


@login_required
def offre_paye(request, pk):
    offre = get_object_or_404(Offre, pk=pk)
    if offre.proposition.cagnotte.responsable != request.user or not offre.valide:
        raise PermissionDenied
    offre.paye = True
    offre.save()
    messages.success(request, f'L’offre {offre.pk} a bien été marquée comme payée !')
    return redirect(offre.proposition.cagnotte)
