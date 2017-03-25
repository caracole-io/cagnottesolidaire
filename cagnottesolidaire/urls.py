from django.conf import settings
from django.conf.urls import include, url
from django.conf.urls.static import static
from django.contrib import admin

from registration.backends.default.views import RegistrationView

from .forms import RegistrationFormFullName

urlpatterns = [
    url(r'^admin/', admin.site.urls),
    url(r'^accounts/register/$', RegistrationView.as_view(form_class=RegistrationFormFullName),
        name='registration_register'),
    url(r'^accounts/', include('registration.backends.default.urls')),
    url(r'^', include('projets.urls')),
]

if settings.DEBUG:
    urlpatterns += static(settings.MEDIA_URL, document_root=settings.MEDIA_ROOT)  # pragma: no cover
