"""Main views."""
from datetime import date
from typing import Any, Dict

from django.conf import settings
from django.contrib import messages
from django.contrib.auth.decorators import login_required
from django.contrib.auth.mixins import LoginRequiredMixin
from django.core.exceptions import PermissionDenied
from django.core.mail import mail_admins
from django.db.models import QuerySet
from django.http import HttpRequest, HttpResponse
from django.shortcuts import get_object_or_404, redirect
from django.template.loader import get_template
from django.views.generic import CreateView, DeleteView, DetailView, ListView

from .forms import CagnotteForm, OffreForm
from .models import Cagnotte, Demande, Offre, Proposition
from .utils import IsUserOrAboveMixin


class CagnotteListView(ListView):
    """A view to list all Cagnottes."""
    model = Cagnotte


class CagnotteCreateView(LoginRequiredMixin, CreateView):
    """A view to create a new Cagnotte."""
    model = Cagnotte
    form_class = CagnotteForm

    def form_valid(self, form) -> HttpResponse:
        """Validate the Cagnotte creation form."""
        form.instance.responsable = self.request.user
        messages.success(self.request, 'Votre cagnotte a été correctement créée !')
        return super().form_valid(form)


class CagnotteDetailView(DetailView):
    """View a Cagnotte details."""
    model = Cagnotte

    def get_context_data(self, **kwargs) -> Dict:
        """Add today's date to the context."""
        return super().get_context_data(today=date.today(), **kwargs)


class PropositionCreateView(LoginRequiredMixin, CreateView):
    """A view to create a new Proposition."""
    model = Proposition
    fields = ['name', 'description', 'prix', 'beneficiaires', 'image']

    def form_valid(self, form) -> HttpResponse:
        """Validate the Proposition creation form."""
        cagnotte = get_object_or_404(Cagnotte, slug=self.kwargs.get('slug', None))
        form.instance.cagnotte = cagnotte
        form.instance.responsable = self.request.user
        messages.success(self.request, 'Votre proposition a été correctement ajoutée !')
        return super().form_valid(form)


class PropositionDetailView(DetailView):
    """view a Proposition details."""
    object: Proposition
    model = Proposition

    def get_context_data(self, **kwargs) -> Dict:
        """Add today's date and the Cagnotte to the context."""
        return super().get_context_data(today=date.today(), cagnotte=self.object.cagnotte, **kwargs)


class OffreCreateView(LoginRequiredMixin, CreateView):
    """A view to create a new Offre."""
    model = Offre
    form_class = OffreForm

    def get_proposition(self) -> Proposition:
        """Get the Proposition associated to this Offre."""
        return get_object_or_404(Proposition, slug=self.kwargs.get('slug', None))

    def form_valid(self, form) -> HttpResponse:
        """Validate the Offre creation form."""
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

    def get_context_data(self, **kwargs) -> Dict:
        """Add context to the view."""
        cagnotte = get_object_or_404(Cagnotte, slug=self.kwargs.get('p_slug', None))
        proposition = self.get_proposition()
        count = Offre.objects.filter(proposition=proposition, beneficiaire=self.request.user).count()
        return super().get_context_data(cagnotte=cagnotte,
                                        proposition=proposition,
                                        count=count,
                                        object=proposition,
                                        **kwargs)

    def get_initial(self) -> Dict[str, Any]:
        """Get initial data for the creation form."""
        prop = self.get_proposition()
        return {'prix': prop.prix, 'proposition': prop}


class OffreListView(LoginRequiredMixin, ListView):
    """A view to list the current user's Offres."""
    def get_queryset(self) -> QuerySet:
        """Get only the current user's Offres."""
        return Offre.objects.filter(beneficiaire=self.request.user)


class PropositionListView(LoginRequiredMixin, ListView):
    """A view to list the current user's Propositions."""
    def get_queryset(self) -> QuerySet:
        """Get only the current user's Propositions."""
        return Proposition.objects.filter(responsable=self.request.user)


class OffreDetailView(IsUserOrAboveMixin, DetailView):
    """Show the details of an Offre only for the right users."""
    model = Offre

    def get_user(self):
        """Only the Proposition's responsable (and staff) can see this."""
        return self.get_object().proposition.responsable


class DemandeCreateView(LoginRequiredMixin, CreateView):
    """A view to add a Demande."""
    model = Demande
    fields = ('description', )

    def form_valid(self, form) -> HttpResponse:
        """Validate the Demande creation form."""
        form.instance.demandeur = self.request.user
        form.instance.cagnotte = get_object_or_404(Cagnotte, slug=self.kwargs['slug'])
        messages.success(self.request, 'Votre demande a été correctement enregistrée !')
        return super().form_valid(form)


class DemandeDeleteView(IsUserOrAboveMixin, DeleteView):
    """A view to allow users delete a Demande."""
    object: Demande
    model = Demande

    def get_success_url(self) -> str:
        """On success, return to the list view."""
        return self.object.get_absolute_url()

    def get_user(self):
        """Only the demandeur (or staff) can delete his Demande."""
        return self.get_object().demandeur


@login_required
def offre_ok(request: HttpRequest, pk: int) -> HttpResponse:
    """When a Proposition's responsable accepts an Offre."""
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
def offre_ko(request: HttpRequest, pk: int) -> HttpResponse:
    """When a Proposition's responsable denies an Offre."""
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
def offre_paye(request: HttpRequest, pk: int) -> HttpResponse:
    """When an Offre's payment has been processed."""
    offre = get_object_or_404(Offre, pk=pk)
    if offre.proposition.cagnotte.responsable != request.user or not offre.valide:
        raise PermissionDenied
    offre.paye = True
    offre.save()
    messages.success(request, f'L’offre {offre.pk} a bien été marquée comme payée !')
    return redirect(offre.proposition.cagnotte)
