# catalogo/models.py
from django.db import models
from django.contrib.auth.models import User

# Nota: per ora usiamo il modello User di Django, 
# ma se volessimo espanderlo, potremmo creare un modello CustomUser.

class Maglia(models.Model):
    """
    Modello per rappresentare una singola maglia nella collezione.
    """
    # 1. Proprietario
    # CASCADE significa che se l'utente viene eliminato, tutte le sue maglie vengono eliminate.
    utente = models.ForeignKey(User, on_delete=models.CASCADE)
    
    # 2. Dettagli Base
    squadra = models.CharField(max_length=100, verbose_name="Squadra")
    giocatore = models.CharField(max_length=100, verbose_name="Giocatore")
    # Utilizziamo CharField per l'anno per accettare formati come "2021-2022"
    anno_stagione = models.CharField(max_length=20, verbose_name="Stagione/Anno") 
    
    # 3. Media
    # Le foto saranno caricate nella cartella 'maglie_foto/' all'interno della cartella MEDIA_ROOT
    foto = models.ImageField(upload_to='maglie_foto/', verbose_name="Foto della Maglia")
    
    # 4. Dettagli Aggiuntivi/Finanziari
    dettagli_acquisto = models.TextField(
        blank=True, 
        null=True, 
        verbose_name="Dettagli Acquisto (Dove, Quando, Prezzo Pagato)"
    )
    # Valore stimato (l'utente lo inserisce manualmente)
    valore_stimato = models.DecimalField(
        max_digits=10, 
        decimal_places=2, 
        blank=True, 
        null=True, 
        verbose_name="Valore Stimato (€)"
    )
    
    # 5. Collezionista e Vetrina
    note_personali = models.TextField(
        blank=True, 
        null=True, 
        verbose_name="Note e Storia Personale della Maglia"
    )
    visibile_in_vetrina = models.BooleanField(
        default=False, 
        verbose_name="Mostra in Vetrina Pubblica"
    )
    fonte_esterna_info = models.TextField(
        blank=True, 
        null=True, 
        verbose_name="Informazioni Salienti (Funzione Plus)"
    )
    
    # 6. Timestamp
    data_creazione = models.DateTimeField(auto_now_add=True)

    class Meta:
        verbose_name = "Maglia Sportiva"
        verbose_name_plural = "Maglie Sportive"

    def __str__(self):
        return f"{self.squadra} - {self.giocatore} ({self.anno_stagione})"