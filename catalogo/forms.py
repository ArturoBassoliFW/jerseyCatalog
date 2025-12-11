# catalogo/forms.py
from django import forms
from .models import Maglia
from django.contrib.auth.forms import UserCreationForm

# Definiamo la classe del Form basata sul modello Maglia
class MagliaForm(forms.ModelForm):
    # La classe Meta definisce i metadati (come il modello e i campi da usare)
    class Meta:
        model = Maglia
        
        # Specifichiamo quali campi del modello Maglia vogliamo includere nel form.
        # Escludiamo 'utente' (verrà impostato automaticamente nella vista)
        # e 'data_creazione'/'data_aggiornamento' (gestiti automaticamente dal modello).
        fields = [
            'squadra', 
            'giocatore', 
            'anno_stagione', 
            'foto', 
            'visibile_in_vetrina', 
            'valore_stimato', 
            'dettagli_acquisto', 
            'note_personali', 
            'fonte_esterna_info'
        ]
        
        # Personalizziamo le etichette per renderle più amichevoli
        labels = {
            'squadra': 'Squadra / Club',
            'giocatore': 'Nome Giocatore',
            'anno_stagione': 'Stagione (e.g., 1998/99)',
            'foto': 'Foto della Maglia',
            'visibile_in_vetrina': 'Mostra in Vetrina Pubblica?',
            'valore_stimato': 'Valore Stimato (€)',
            'dettagli_acquisto': 'Dove/Quando è stata acquistata?',
            'note_personali': 'Note Private sulla Maglia',
            'fonte_esterna_info': 'Link o Riferimento Esterno',
        }
        
        # Aggiungiamo attributi HTML per migliorare l'aspetto e l'usabilità
        widgets = {
            'anno_stagione': forms.TextInput(attrs={'placeholder': 'es. 1998/99'}),
            'valore_stimato': forms.NumberInput(attrs={'min': 0}),
            'dettagli_acquisto': forms.Textarea(attrs={'rows': 3}),
            'note_personali': forms.Textarea(attrs={'rows': 3}),
            'fonte_esterna_info': forms.URLInput(attrs={'placeholder': 'https://...'})
        }
        
class RegisterForm(UserCreationForm):
    """
    Estende il form di creazione utente di Django, garantendo 
    che tutti i campi richiesti per la creazione di un utente siano presenti.
    """
    class Meta(UserCreationForm.Meta):
        # Specifica il modello User (che è il default se non modificato in settings)
        # Puoi anche omettere questa riga se usi il modello User predefinito.
        # model = User 
        
        # Puoi aggiungere campi extra se necessario. Per ora, lasciamo i campi di default.
        fields = UserCreationForm.Meta.fields + ('email',) # Esempio: aggiungere il campo email se necessario