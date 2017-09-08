from django.conf.urls import url

from . import views

app_name = 'cagnottesolidaire'
urlpatterns = [
    url(r'^$', views.ProjetListView.as_view(),
        name='projet_list'),
    url(r'^projet$', views.ProjetCreateView.as_view(),
        name='projet_create'),
    url(r'^projet/(?P<slug>[^/]+)$', views.ProjetDetailView.as_view(),
        name='projet'),
    url(r'^projet/(?P<slug>[^/]+)/proposition$', views.PropositionCreateView.as_view(),
        name='proposition_create'),
    url(r'^projet/(?P<p_slug>[^/]+)/proposition/(?P<slug>[^/]+)$', views.PropositionDetailView.as_view(),
        name='proposition'),
    url(r'^projet/(?P<p_slug>[^/]+)/proposition/(?P<slug>[^/]+)/offre$', views.OffreCreateView.as_view(),
        name='offre_create'),
    url(r'^offres$', views.OffreListView.as_view(),
        name='offre_list'),
    url(r'^offre/(?P<pk>\d+)$', views.OffreDetailView.as_view(),
        name='offre'),
    url(r'^offre/(?P<pk>\d+)/ok$', views.offre_ok,
        name='offre_ok'),
    url(r'^offre/(?P<pk>\d+)/ko$', views.offre_ko,
        name='offre_ko'),
    url(r'^offre/(?P<pk>\d+)/paye$', views.offre_paye,
        name='offre_paye'),
    url(r'^propositions$', views.PropositionListView.as_view(),
        name='proposition_list'),
]
