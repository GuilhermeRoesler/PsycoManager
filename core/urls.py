from django.contrib import admin
from django.urls import path, include
from django.views.generic import RedirectView

from django.conf import settings
from django.conf.urls.static import static

urlpatterns = [
    path('', RedirectView.as_view(pattern_name='pacientes', permanent=False)),
    path('admin/', admin.site.urls),
    path('pacientes/', include('pacientes.urls')),
] + static(settings.MEDIA_URL, document_root=settings.MEDIA_ROOT)
