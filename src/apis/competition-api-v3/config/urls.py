"""
URL configuration for config project.

The `urlpatterns` list routes URLs to views. For more information please see:
    https://docs.djangoproject.com/en/6.0/topics/http/urls/
Examples:
Function views
    1. Add an import:  from my_app import views
    2. Add a URL to urlpatterns:  path('', views.home, name='home')
Class-based views
    1. Add an import:  from other_app.views import Home
    2. Add a URL to urlpatterns:  path('', Home.as_view(), name='home')
Including another URLconf
    1. Import the include() function: from django.urls import include, path
    2. Add a URL to urlpatterns:  path('blog/', include('blog.urls'))
"""

from apps.views import HealthView
from django.contrib import admin
from django.urls import include, path
from drf_spectacular.views import (
    SpectacularAPIView,
    SpectacularRedocView,
    SpectacularSwaggerView,
)

from .settings import API_ENDPOINT_PREFIX

urlpatterns = [
    path("", include("django_prometheus.urls")),
    path("admin/", admin.site.urls),
    # Health check endpoint
    path(f"{API_ENDPOINT_PREFIX}/health/", HealthView.as_view(), name="health"),
    # API schema and documentation endpoints
    path(f"{API_ENDPOINT_PREFIX}/schema/", SpectacularAPIView.as_view(), name="schema"),
    path(
        f"{API_ENDPOINT_PREFIX}/schema/swagger-ui/",
        SpectacularSwaggerView.as_view(url_name="schema"),
        name="swagger-ui",
    ),
    path(
        f"{API_ENDPOINT_PREFIX}/schema/redoc/",
        SpectacularRedocView.as_view(url_name="schema"),
        name="redoc",
    ),
]
