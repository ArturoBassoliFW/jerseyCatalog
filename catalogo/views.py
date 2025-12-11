# catalogo/views.py
from django.shortcuts import render, get_object_or_404, redirect
from django.contrib.auth.decorators import login_required 
from django.contrib import messages
from django.http import Http404 
from .models import Maglia
from .forms import MagliaForm, RegisterForm 
from django.db.models import Q
from django.core.paginator import Paginator, EmptyPage, PageNotAnInteger
from django.db.models import Count

# --------------------------
# 1. Vetrina Pubblica (Home Page)
# --------------------------
def vetrina_pubblica(request):
    """
    Mostra tutte le maglie pubbliche, con supporto per la ricerca.
    """
    
    # Iniziamo con il QuerySet di base (solo maglie visibili in vetrina)
    maglie_pubbliche = Maglia.objects.filter(visibile_in_vetrina=True)
    
    # 1. Otteniamo il termine di ricerca dalla richiesta (query string)
    query = request.GET.get('q') 
    
    # 1. Otteniamo il parametro di ordinamento richiesto dall'URL (default: stagione decrescente)
    sort_by = request.GET.get('sort', '-anno_stagione')
    
    # Definiamo le opzioni di ordinamento valide per motivi di sicurezza
    valid_sort_fields = [
        'giocatore', '-giocatore', 
        'squadra', '-squadra', 
        'anno_stagione', '-anno_stagione',
        'data_creazione', '-data_creazione'
    ]
    
    # 2. Applichiamo l'ordinamento solo se il campo è valido
    if sort_by in valid_sort_fields:
        maglie_pubbliche = maglie_pubbliche.order_by(sort_by)
    else:
        # Se il campo non è valido o manca, usiamo il default (stagione decrescente)
        maglie_pubbliche = maglie_pubbliche.order_by('-anno_stagione')
        sort_by = '-anno_stagione' # Impostiamo il valore corretto per il template
    
    if query:
        # 2. Se è presente un termine di ricerca, filtriamo il QuerySet.
        # Usiamo l'oggetto Q per combinare condizioni con OR (|)
        # e il lookup __icontains per cercare in modo case-insensitive
        # (ignora maiuscole/minuscole) e parziale (contiene il testo).
        
        filtro_ricerca = (
            Q(squadra__icontains=query) |
            Q(giocatore__icontains=query) |
            Q(anno_stagione__icontains=query)
        )
        
        maglie_pubbliche = maglie_pubbliche.filter(filtro_ricerca)
    
    # 1. Creiamo l'oggetto Paginator: 9 elementi per pagina
    paginator = Paginator(maglie_pubbliche, 9) 
    
    # 2. Otteniamo il numero di pagina richiesto dall'URL (default: 1)
    page = request.GET.get('page') 
    
    try:
        # 3. Otteniamo l'oggetto Page (contiene le maglie della pagina corrente)
        maglie_page = paginator.page(page)
    except PageNotAnInteger:
        # Se la pagina non è un numero intero, visualizza la prima pagina.
        maglie_page = paginator.page(1)
    except EmptyPage:
        # Se la pagina è fuori intervallo (e.g., 999), visualizza l'ultima pagina.
        maglie_page = paginator.page(paginator.num_pages)
        
    context = {
        # Passiamo al template l'oggetto Page, NON l'intero QuerySet
        'maglie': maglie_page, 
        'titolo_pagina': "Vetrina Pubblica di Collezioni di Maglie",
        'query': query,
        'sort_by': sort_by,
    }
    
    return render(request, 'catalogo/vetrina_pubblica.html', context)


# --------------------------
# 2. Vetrina Dettaglio Maglia (Vista Pubblica/Privata)
# --------------------------
def dettaglio_maglia(request, pk):
    """
    Mostra i dettagli di una singola maglia.
    Limita la visualizzazione dei dettagli privati solo al proprietario.
    """
    # Recupera la maglia, non è necessario filtrare per utente qui, perché vogliamo 
    # che tutti possano vedere i dettagli pubblici (se la maglia è pubblica).
    maglia = get_object_or_404(Maglia, pk=pk)
    
    # Controllo di sicurezza: se la maglia NON è visibile in vetrina, 
    # può essere vista solo dal proprietario.
    if not maglia.visibile_in_vetrina:
        # Se la maglia non è pubblica E l'utente non è loggato O l'utente loggato non è il proprietario
        if not request.user.is_authenticated or maglia.utente != request.user:
            # Reindirizziamo l'utente alla pagina di login o a una pagina di errore.
            # In questo caso, lo reindirizziamo alla dashboard (se loggato) o alla vetrina.
            # La soluzione più sicura in questo contesto è sollevare un 404.
            # Usiamo un PermissionDenied (o semplicemente lasciamo sollevare l'eccezione, ma il 404 è standard)
            
            # Una soluzione più semplice per il nostro progetto: assicuriamo che l'utente sia il proprietario
            if maglia.utente != request.user:
                # Per maglie private, solo il proprietario può vederle.
                # Se non è il proprietario, restituiamo un 404
                raise Http404("La maglia richiesta non esiste o non è pubblica.") 
    
    # Variabile booleana utile nel template per sapere se mostrare i dati sensibili
    is_owner = maglia.utente == request.user
    
    context = {
        'maglia': maglia,
        'titolo_pagina': f"{maglia.squadra} - {maglia.giocatore}",
        'is_owner': is_owner, # Variabile per il template
    }
    
    return render(request, 'catalogo/dettaglio_maglia.html', context)

# --------------------------
# 3. Dashboard Privata (Protetta da login)
# --------------------------
@login_required 
def dashboard(request):
    """
    Mostra tutte le maglie appartenenti all'utente loggato.
    """
    # Filtra il modello Maglia per trovare solo quelle il cui campo 'utente' è l'utente loggato
    mie_maglie = Maglia.objects.filter(utente=request.user).order_by('-id')
    
    context = {
        'maglie': mie_maglie,
        'titolo_pagina': f"Dashboard di {request.user.username}"
    }
    
    return render(request, 'catalogo/dashboard.html', context)

# --------------------------
# 4. Aggiungi Nuova Maglia (Creazione)
# --------------------------
@login_required 
def aggiungi_maglia(request):
    """
    Gestisce la creazione di una nuova maglia tramite il form.
    """
    if request.method == 'POST':
        # Se la richiesta è POST (invio del modulo):
        # Passiamo i dati inviati (request.POST) e i file (request.FILES) al form
        form = MagliaForm(request.POST, request.FILES) 
        
        if form.is_valid():
            # 1. Non salvare subito: prima assegniamo l'utente!
            nuova_maglia = form.save(commit=False)
            
            # 2. Impostiamo l'utente proprietario come l'utente loggato
            nuova_maglia.utente = request.user
            
            # 3. Salviamo finalmente l'oggetto nel database
            nuova_maglia.save()
            
            # Aggiungiamo un messaggio di successo
            messages.success(request, f"La maglia di {nuova_maglia.giocatore} è stata aggiunta alla tua collezione!")
            
            # Reindirizziamo l'utente alla Dashboard
            return redirect('dashboard')
            
    else:
        # Se la richiesta è GET (prima apertura del modulo):
        # Creiamo un form vuoto
        form = MagliaForm()
        
    context = {
        'form': form,
        'titolo_pagina': "Aggiungi Nuova Maglia",
        'action': 'Aggiungi' # Usato per il testo del bottone
    }
    
    # Renderizziamo il template con il form
    return render(request, 'catalogo/maglia_form.html', context)

# --------------------------
# 5. Modifica Maglia (Update)
# --------------------------
@login_required
def modifica_maglia(request, pk):
    """
    Gestisce la modifica di una maglia esistente.
    """
    # 1. Recupera l'oggetto Maglia o solleva un 404.
    # Usiamo get_object_or_404 per trovare la maglia E verificarne il proprietario (sicurezza!).
    maglia = get_object_or_404(Maglia, pk=pk, utente=request.user)
    
    if request.method == 'POST':
        # Se la richiesta è POST:
        # Passiamo i dati inviati, i file E l'istanza della maglia esistente.
        # Questo dice a Django di AGGIORNARE l'oggetto esistente, non crearne uno nuovo.
        form = MagliaForm(request.POST, request.FILES, instance=maglia)
        
        if form.is_valid():
            # Il campo 'utente' è già impostato, quindi possiamo salvare direttamente.
            form.save()
            
            # Messaggio di successo
            messages.success(request, f"La maglia di {maglia.giocatore} è stata aggiornata con successo!")
            
            # Reindirizziamo l'utente alla Dashboard
            return redirect('dashboard')
            
    else:
        # Se la richiesta è GET (prima apertura del modulo):
        # Creiamo il form popolandolo con i dati della maglia esistente.
        form = MagliaForm(instance=maglia)
        
    context = {
        'form': form,
        'titolo_pagina': f"Modifica Maglia: {maglia.giocatore}",
        'action': 'Salva Modifiche' # Usato per il testo del bottone
    }
    
    # Riutilizziamo lo stesso template della creazione: 'catalogo/maglia_form.html'
    return render(request, 'catalogo/maglia_form.html', context)

# --------------------------
# 6. Elimina Maglia (Delete)
# --------------------------
@login_required
def elimina_maglia(request, pk):
    """
    Gestisce l'eliminazione di una maglia, includendo una richiesta di conferma.
    """
    # 1. Recupera l'oggetto Maglia, verificando che appartenga all'utente loggato.
    maglia = get_object_or_404(Maglia, pk=pk, utente=request.user)
    
    if request.method == 'POST':
        # 2. Se la richiesta è POST, l'utente ha confermato l'eliminazione.
        
        # Salviamo il nome del giocatore prima di eliminare l'oggetto
        nome_giocatore = maglia.giocatore
        
        # Esegue l'eliminazione dal database
        maglia.delete() 
        
        # Messaggio di successo
        messages.success(request, f"La maglia di {nome_giocatore} è stata rimossa dalla tua collezione.")
        
        # Reindirizziamo l'utente alla Dashboard
        return redirect('dashboard')
        
    # Se la richiesta è GET, mostriamo la pagina di conferma
    context = {
        'maglia': maglia,
        'titolo_pagina': "Conferma Eliminazione",
    }
    
    # Renderizziamo il template di conferma
    return render(request, 'catalogo/maglia_conferma_elimina.html', context)

# --------------------------
# 7. Statistiche della Collezione (Protetta da login)
# --------------------------
@login_required
def statistiche_collezione(request):
    """
    Mostra un riepilogo statistico della collezione dell'utente loggato.
    """
    
    # QuerySet base: solo le maglie dell'utente corrente
    maglie_utente = Maglia.objects.filter(utente=request.user)
    
    # 1. Statistiche Base
    statistiche = {
        'totale_maglie': maglie_utente.count(),
        'maglie_pubbliche': maglie_utente.filter(visibile_in_vetrina=True).count(),
        'maglie_private': maglie_utente.filter(visibile_in_vetrina=False).count(),
        'prima_maglia': maglie_utente.order_by('id').first(),
        'ultima_maglia': maglie_utente.order_by('-id').first(),
    }
    
    # 2. Squadre più Comuni (Top 5)
    squadre_popolari = maglie_utente.values('squadra') \
                                   .annotate(conteggio=Count('squadra')) \
                                   .order_by('-conteggio')[:5]
    
    # 3. Anni di Stagione (Raggruppamento)
    anni_stagione = maglie_utente.values('anno_stagione') \
                                .annotate(conteggio=Count('anno_stagione')) \
                                .order_by('-anno_stagione')

    context = {
        'statistiche': statistiche,
        'squadre_popolari': squadre_popolari,
        'anni_stagione': anni_stagione,
        'titolo_pagina': "Statistiche della Tua Collezione 📈",
    }
    
    return render(request, 'catalogo/statistiche.html', context)

# --------------------------
# 8. Registrazione Utente (Vista Pubblica)
# --------------------------
def register_user(request): # <-- Questa vista mancava
    """
    Gestisce la registrazione di un nuovo utente.
    """
    if request.user.is_authenticated:
        # Se l'utente è già loggato, reindirizzalo alla Dashboard
        messages.info(request, "Sei già loggato.")
        return redirect('dashboard')
        
    if request.method == 'POST':
        # Passiamo al form i dati inviati dalla richiesta POST
        form = RegisterForm(request.POST) 
        
        if form.is_valid():
            form.save() # Salva il nuovo utente nel database
            username = form.cleaned_data.get('username')
            messages.success(request, f"Account creato per **{username}**! Ora puoi accedere.")
            # Reindirizza l'utente alla pagina di login
            return redirect('login') 
            
    else:
        # Richiesta GET: mostra il form vuoto
        form = RegisterForm()
        
    context = {
        'form': form,
        'titolo_pagina': "Registrazione Utente",
    }
    
    # Renderizza un template che userai per mostrare il form di registrazione
    return render(request, 'catalogo/register.html', context)