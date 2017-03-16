from django.conf.urls import url

from .views import ProjetCreateView, ProjetListView

app_name = 'projets'
urlpatterns = [
    url(r'^$', ProjetListView.as_view(), name='list_projet'),
    url(r'^projet$', ProjetCreateView.as_view(), name='create_projet'),
]
