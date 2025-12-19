# catalogo/urls.py
from django.urls import path
from . import views

urlpatterns = [
    # Vetrina Pubblica
    path('', views.vetrina_pubblica, name='vetrina_pubblica'),
    
    # Registrazione Utente
    path('register/', views.register_user, name='register'),
    
    # Dashboard del Collezionista (privata)
    path('dashboard/', views.dashboard, name='dashboard'), # <--- NUOVO PERCORSO
    
    # Aggiungi Maglia (privata)
    path('dashboard/aggiungi/', views.aggiungi_maglia, name='aggiungi_maglia'),
    
    # Modifica Maglia (privata)
    path('dashboard/modifica/<int:pk>/', views.modifica_maglia, name='modifica_maglia'),
    
    # Elimina Maglia (privata)
    path('dashboard/elimina/<int:pk>/', views.elimina_maglia, name='elimina_maglia'),
    
    # Vetrina Dettaglio Maglia
    path('maglia/<int:pk>/', views.dettaglio_maglia, name='dettaglio_maglia'),
    
    # Statistiche Collezione (privata)
    path('statistiche/', views.statistiche, name='statistiche'),
]