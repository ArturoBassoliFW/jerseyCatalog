# catalogo/admin.py
from django.contrib import admin
from .models import Maglia

# 1. Definiamo come vogliamo che la Maglia appaia nel pannello admin (Opzionale, ma consigliato)
class MagliaAdmin(admin.ModelAdmin):
    # Mostra queste colonne nella lista delle maglie
    list_display = ('giocatore', 'squadra', 'anno_stagione', 'utente', 'valore_stimato', 'visibile_in_vetrina')
    
    # Filtri laterali per trovare rapidamente le maglie
    list_filter = ('squadra', 'anno_stagione', 'visibile_in_vetrina')
    
    # Campo di ricerca
    search_fields = ('giocatore', 'squadra', 'note_personali')
    
    # Suddividi i campi in gruppi per maggiore leggibilità nella pagina di modifica
    fieldsets = (
        ('Informazioni Base', {
            'fields': ('utente', 'squadra', 'giocatore', 'anno_stagione', 'foto')
        }),
        ('Dettagli Acquisto e Valore', {
            'fields': ('dettagli_acquisto', 'valore_stimato')
        }),
        ('Note e Vetrina', {
            'fields': ('note_personali', 'visibile_in_vetrina', 'fonte_esterna_info'),
            'classes': ('collapse',), # Rende questa sezione apribile/chiudibile
        })
    )

# 2. Registriamo il modello usando la configurazione personalizzata
admin.site.register(Maglia, MagliaAdmin)