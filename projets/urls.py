from django.conf.urls import url

from .views import ProjetCreateView, ProjetDetailView, ProjetListView

app_name = 'projets'
urlpatterns = [
    url(r'^$', ProjetListView.as_view(), name='projet_list'),
    url(r'^projet$', ProjetCreateView.as_view(), name='projet_create'),
    url(r'^projet/(?P<slug>[^/]+)$', ProjetDetailView.as_view(), name='projet'),
]
