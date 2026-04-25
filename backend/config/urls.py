"""
URL configuration for movies_vault project.


The `urlpatterns` list routes URLs to views. For more information please see:
    https://docs.djangoproject.com/en/4.2/topics/http/urls/
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

from django.contrib import admin
from django.urls import path, include
from core.health_views import health_check, health_page

urlpatterns = [
    path("admin/", admin.site.urls),
    
    # Health check endpoints (for monitoring and manual checks)
    path("health/", health_check, name="health_check"),
    path("", health_page, name="health_page"),  # Root URL shows health page
    
    # API routes
    path("api/auth/", include("authentication.urls")),
    path("api/movies/", include("movies.urls")),
    path("api/watchlist/", include("watchlist.urls")),
    path("api/core/", include("core.urls")),
]
