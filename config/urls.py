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
# config/urls.py
from django.contrib import admin
from django.urls import path, include 
from django.conf import settings # Importiamo settings per la gestione dei media
from django.conf.urls.static import static # Importiamo static per la gestione dei media

urlpatterns = [
    path('admin/', admin.site.urls),
    
    # URL di Autenticazione (login, logout, password reset, ecc.)
    # Verranno accessibili tramite l'indirizzo /account/login, /account/logout, ecc.
    path('account/', include('django.contrib.auth.urls')), 
    
    # URL della nostra app catalogo (homepage e vetrina pubblica)
    path('', include('catalogo.urls')), 
]

# Configurazione per servire i file media (immagini) solo in modalità di sviluppo (DEBUG=True)
if settings.DEBUG:
    urlpatterns += static(settings.MEDIA_URL, document_root=settings.MEDIA_ROOT)