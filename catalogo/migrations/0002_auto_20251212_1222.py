from django.db import migrations

def create_initial_superuser(apps, schema_editor):
    from django.contrib.auth import get_user_model
    User = get_user_model()
    
    USERNAME = 'Admin' 
    EMAIL = 'arturo.bassoli@freshways.it'
    PASSWORD = 'GwR*dc1RF4FBg0&*AXG7' 
    
    # 1. Tenta di trovare l'utente
    try:
        user = User.objects.get(username=USERNAME)
        print(f"Utente {USERNAME} trovato. Aggiornamento permessi...")
    except User.DoesNotExist:
        # 2. Se non esiste, crealo come superuser (ha già i permessi giusti)
        user = User.objects.create_superuser(
            username=USERNAME,
            email=EMAIL, 
            password=PASSWORD
        )
        print(f"Superutente {USERNAME} creato.")
        
    # 3. FORZA SEMPRE i permessi (Risolve il problema "not authorized")
    if not user.is_superuser or not user.is_staff:
        user.is_superuser = True
        user.is_staff = True
        user.save()
        print(f"Permessi di Superuser e Staff aggiornati per {USERNAME}.")
        

class Migration(migrations.Migration):

    dependencies = [
        ('catalogo', '0001_initial'), 
    ]

    operations = [
        migrations.RunPython(create_initial_superuser),
    ]