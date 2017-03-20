from django.conf.urls import url

from .views import (OffreCreateView, OffreListView, ProjetCreateView, ProjetDetailView,
                    ProjetListView, PropositionCreateView, PropositionDetailView, PropositionListView)

app_name = 'projets'
urlpatterns = [
    url(r'^$', ProjetListView.as_view(),
        name='projet_list'),
    url(r'^projet$', ProjetCreateView.as_view(),
        name='projet_create'),
    url(r'^projet/(?P<slug>[^/]+)$', ProjetDetailView.as_view(),
        name='projet'),
    url(r'^projet/(?P<slug>[^/]+)/proposition$', PropositionCreateView.as_view(),
        name='proposition_create'),
    url(r'^projet/(?P<p_slug>[^/]+)/proposition/(?P<slug>[^/]+)$', PropositionDetailView.as_view(),
        name='proposition'),
    url(r'^projet/(?P<p_slug>[^/]+)/proposition/(?P<slug>[^/]+)/offre$', OffreCreateView.as_view(),
        name='offre_create'),
    url(r'^offres$', OffreListView.as_view(),
        name='offre_list'),
    url(r'^propositions$', PropositionListView.as_view(),
        name='proposition_list'),
]
