from django.db import migrations
# Non abbiamo bisogno di importare get_user_model qui, lo facciamo nella funzione RunPython

def create_initial_superuser(apps, schema_editor):
    """
    Crea un superutente iniziale se non ne esiste nessuno.
    Questa funzione viene eseguita all'applicazione della migrazione.
    """
    # Importa il modello User nello scope della migrazione
    from django.contrib.auth import get_user_model
    User = get_user_model()
    
    USERNAME = 'Admin' 
    EMAIL = 'arturo.bassoli@freshways.it'
    PASSWORD = 'GwR*dc1RF4FBg0&*AXG7' 
    
    # Verifica se l'utente esiste già per evitare errori su deploy successivi
    if not User.objects.filter(username=USERNAME).exists():
        print(f"Creazione Superutente: {USERNAME}")
        User.objects.create_superuser(
            username=USERNAME,
            email=EMAIL, 
            password=PASSWORD
        )

class Migration(migrations.Migration):

    dependencies = [
        # Assicurati che questo puntatore sia CORRETTO
        # Se hai altre migrazioni tra 0001 e il tuo file, usa l'ultima creata!
        ('catalogo', '0001_initial'), 
    ]

    operations = [
        # Esegue la funzione Python per creare l'utente
        migrations.RunPython(create_initial_superuser),
    ]