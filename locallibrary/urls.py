"""locallibrary URL Configuration

The `urlpatterns` list routes URLs to views. For more information please see:
    https://docs.djangoproject.com/en/4.1/topics/http/urls/
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
from django.urls import include
from django.views.generic import RedirectView
from django.conf import settings
from django.conf.urls.static import static

urlpatterns = [
    path("admin/", admin.site.urls),
    path('catalog/', include('catalog.urls')), # Source the file locallibrary/catalog/urls.py for more url patterns
    path('', RedirectView.as_view(url='catalog/', permanent=True)), # Redirect website root http://127.0.0.1:8000/ to http://127.0.0.1:8000/catalog/
]

# Serve static files during development
urlpatterns += static(settings.STATIC_URL, document_root=settings.STATIC_ROOT)

# Add Django site authentication urls (for login, logout, password management)
# The below enables all of the below URL mappings:
#accounts/ login/ [name='login']
#accounts/ logout/ [name='logout']
#accounts/ password_change/ [name='password_change']
#accounts/ password_change/done/ [name='password_change_done']
#accounts/ password_reset/ [name='password_reset']
#accounts/ password_reset/done/ [name='password_reset_done']
#accounts/ reset/<uidb64>/<token>/ [name='password_reset_confirm']
#accounts/ reset/done/ [name='password_reset_complete']
urlpatterns += [
    path('accounts/', include('django.contrib.auth.urls')),
]