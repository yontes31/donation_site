"""
URL configuration for donation_site project.

The `urlpatterns` list routes URLs to views. For more information please see:
    https://docs.djangoproject.com/en/5.1/topics/http/urls/
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
from django.urls import path
from django.conf import settings
from django.conf.urls.static import static
from locations import views  # Add this line to import views from locations app

urlpatterns = [
    path('admin/', admin.site.urls),
    path('', views.home, name='home'),  # Add this line for the home page
    path('donate/', views.donation_view, name='donation_view'),
    path('create-post/', views.create_post_view, name='create_post_view'),
    path('api/donation/search/', views.donation_view, name='api_donation_search'),  # Add API endpoint
    path('api/vote/', views.vote_location, name='api_vote'),  # Add voting API endpoint
] + static(settings.MEDIA_URL, document_root=settings.MEDIA_ROOT)
