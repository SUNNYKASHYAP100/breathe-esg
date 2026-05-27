"""
URL configuration for Breathe ESG backend.
"""

from django.contrib import admin
from django.urls import path, include
from django.http import HttpResponse

from drf_spectacular.views import (
    SpectacularAPIView,
    SpectacularSwaggerView
)


def home(request):
    return HttpResponse("Breathe ESG Backend Running Successfully 🚀")


urlpatterns = [
    path('', home),

    path('admin/', admin.site.urls),

    path(
        'api/schema/',
        SpectacularAPIView.as_view(),
        name='schema'
    ),

    path(
        'api/docs/',
        SpectacularSwaggerView.as_view(url_name='schema'),
        name='swagger-ui'
    ),

    path('api/tenants/', include('apps.tenants.urls')),
    path('api/ingestion/', include('apps.ingestion.urls')),
    path('api/review/', include('apps.review.urls')),
]