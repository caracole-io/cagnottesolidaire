"""URLs for the Cagnotte Solidaire django app."""
from django.urls import path

from . import views

app_name = "cagnottesolidaire"
urlpatterns = [
    path("", views.CagnotteListView.as_view(), name="cagnotte_list"),
    path("cagnotte", views.CagnotteCreateView.as_view(), name="cagnotte_create"),
    path("cagnotte/<str:slug>", views.CagnotteDetailView.as_view(), name="cagnotte"),
    path(
        "cagnotte/<str:slug>/proposition",
        views.PropositionCreateView.as_view(),
        name="proposition_create",
    ),
    path(
        "cagnotte/<str:p_slug>+)/proposition/<str:slug>",
        views.PropositionDetailView.as_view(),
        name="proposition",
    ),
    path(
        "cagnotte/<str:p_slug>/proposition/<str:slug>/offre",
        views.OffreCreateView.as_view(),
        name="offre_create",
    ),
    path("offres", views.OffreListView.as_view(), name="offre_list"),
    path("offre/<int:pk>", views.OffreDetailView.as_view(), name="offre"),
    path("offre/<int:pk>/ok", views.offre_ok, name="offre_ok"),
    path("offre/<int:pk>/ko", views.offre_ko, name="offre_ko"),
    path("offre/<int:pk>/paye", views.offre_paye, name="offre_paye"),
    path("propositions", views.PropositionListView.as_view(), name="proposition_list"),
    path(
        "demande/<str:slug>",
        views.DemandeCreateView.as_view(),
        name="demande_create",
    ),
    path(
        "demande/del/<int:pk>",
        views.DemandeDeleteView.as_view(),
        name="demande_delete",
    ),
]
