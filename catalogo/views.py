# catalogo/views.py
from django.shortcuts import render, get_object_or_404, redirect
from django.contrib.auth.decorators import login_required 
from django.contrib import messages
from django.http import Http404 
from django.urls import reverse
from .models import Maglia
from .forms import MagliaForm, RegisterForm 
from django.db.models import Q, Count
from django.core.paginator import Paginator, EmptyPage, PageNotAnInteger
from django.contrib.auth.models import User  # Fondamentale per il filtro utente

# --------------------------
# 1. Vetrina Pubblica (Home Page)
# --------------------------
def vetrina_pubblica(request):
    """
    Mostra tutte le maglie pubbliche con supporto per ricerca, 
    ordinamento e filtro per specifico utente.
    """
    # 1. Recupero parametri dalla URL
    query = request.GET.get('q')
    sort_by = request.GET.get('sort', '-data_creazione')
    utente_id = request.GET.get('utente')
    
    # 2. QuerySet di base (solo maglie pubbliche)
    maglie_pubbliche = Maglia.objects.filter(visibile_in_vetrina=True)
    
    # 3. Filtro per Utente (Collezionista)
    if utente_id:
        maglie_pubbliche = maglie_pubbliche.filter(utente_id=utente_id)

    # 4. Filtro Ricerca Testuale (Q objects)
    if query:
        filtro_ricerca = (
            Q(squadra__icontains=query) |
            Q(giocatore__icontains=query) |
            Q(anno_stagione__icontains=query)
        )
        maglie_pubbliche = maglie_pubbliche.filter(filtro_ricerca)

    # 5. Ordinamento Sicuro
    valid_sort_fields = [
        'giocatore', '-giocatore', 
        'squadra', '-squadra', 
        'anno_stagione', '-anno_stagione',
        'data_creazione', '-data_creazione'
    ]
    
    if sort_by not in valid_sort_fields:
        sort_by = '-data_creazione' # Fallback se il parametro è manomesso
    
    maglie_pubbliche = maglie_pubbliche.order_by(sort_by)

    # 6. Dati per i Dropdown del template
    # Prendiamo solo gli utenti che hanno effettivamente almeno una maglia pubblica
    utenti_con_maglie = User.objects.filter(maglia__visibile_in_vetrina=True).distinct()
    
    # 7. Paginazione (9 elementi per pagina)
    paginator = Paginator(maglie_pubbliche, 9) 
    page = request.GET.get('page') 
    
    try:
        maglie_page = paginator.page(page)
    except PageNotAnInteger:
        maglie_page = paginator.page(1)
    except EmptyPage:
        maglie_page = paginator.page(paginator.num_pages)
        
    context = {
        'maglie': maglie_page, 
        'titolo_pagina': "Vetrina della Community",
        'query': query,
        'sort_by': sort_by,
        'selected_utente': utente_id,
        'utenti_con_maglie': utenti_con_maglie,
    }
    
    return render(request, 'catalogo/vetrina_pubblica.html', context)


# --------------------------
# 2. Vetrina Dettaglio Maglia
# --------------------------
def dettaglio_maglia(request, pk):
    maglia = get_object_or_404(Maglia, pk=pk)
    
    # Controllo privacy
    if not maglia.visibile_in_vetrina:
        if not request.user.is_authenticated or maglia.utente != request.user:
            raise Http404("La maglia richiesta non esiste o è privata.") 
    
    # Gestione pulsante "Torna indietro"
    back_url = request.META.get('HTTP_REFERER')
    if not back_url or request.build_absolute_uri() in back_url:
        back_url = reverse('vetrina_pubblica')

    context = {
        'maglia': maglia,
        'titolo_pagina': f"{maglia.squadra} - {maglia.giocatore}",
        'is_owner': maglia.utente == request.user,
        'back_url': back_url,
    }
    return render(request, 'catalogo/dettaglio_maglia.html', context)

# --------------------------
# 3. Dashboard Privata
# --------------------------
@login_required 
def dashboard(request):
    mie_maglie = Maglia.objects.filter(utente=request.user).order_by('-id')
    context = {
        'maglie': mie_maglie,
        'titolo_pagina': f"Dashboard di {request.user.username}"
    }
    return render(request, 'catalogo/dashboard.html', context)

# --------------------------
# 4. Aggiungi Nuova Maglia
# --------------------------
@login_required 
def aggiungi_maglia(request):
    if request.method == 'POST':
        form = MagliaForm(request.POST, request.FILES) 
        if form.is_valid():
            nuova_maglia = form.save(commit=False)
            nuova_maglia.utente = request.user
            nuova_maglia.save()
            messages.success(request, f"La maglia di {nuova_maglia.giocatore} è stata aggiunta!")
            return redirect('dashboard')
    else:
        form = MagliaForm()
        
    context = {
        'form': form,
        'titolo_pagina': "Aggiungi Nuova Maglia",
        'action': 'Aggiungi'
    }
    return render(request, 'catalogo/maglia_form.html', context)

# --------------------------
# 5. Modifica Maglia
# --------------------------
@login_required
def modifica_maglia(request, pk):
    maglia = get_object_or_404(Maglia, pk=pk, utente=request.user)
    if request.method == 'POST':
        form = MagliaForm(request.POST, request.FILES, instance=maglia)
        if form.is_valid():
            form.save()
            messages.success(request, f"La maglia di {maglia.giocatore} è stata aggiornata!")
            return redirect('dashboard')
    else:
        form = MagliaForm(instance=maglia)
        
    context = {
        'form': form,
        'titolo_pagina': f"Modifica Maglia: {maglia.giocatore}",
        'action': 'Salva Modifiche'
    }
    return render(request, 'catalogo/maglia_form.html', context)

# --------------------------
# 6. Elimina Maglia
# --------------------------
@login_required
def elimina_maglia(request, pk):
    maglia = get_object_or_404(Maglia, pk=pk, utente=request.user)
    if request.method == 'POST':
        nome_giocatore = maglia.giocatore
        maglia.delete() 
        messages.success(request, f"La maglia di {nome_giocatore} è stata rimossa.")
        return redirect('dashboard')
        
    context = {
        'maglia': maglia,
        'titolo_pagina': "Conferma Eliminazione",
    }
    return render(request, 'catalogo/maglia_conferma_elimina.html', context)

# --------------------------
# 7. Statistiche
# --------------------------
@login_required
def statistiche(request):
    maglie_utente = Maglia.objects.filter(utente=request.user)
    
    stats_data = {
        'totale_maglie': maglie_utente.count(),
        'maglie_pubbliche': maglie_utente.filter(visibile_in_vetrina=True).count(),
        'maglie_private': maglie_utente.filter(visibile_in_vetrina=False).count(),
        'prima_maglia': maglie_utente.order_by('id').first(),
        'ultima_maglia': maglie_utente.order_by('-id').first(),
    }
    
    squadre_popolari = maglie_utente.values('squadra').annotate(conteggio=Count('squadra')).order_by('-conteggio')[:5]
    anni_stagione = maglie_utente.values('anno_stagione').annotate(conteggio=Count('anno_stagione')).order_by('-anno_stagione')

    context = {
        'statistiche': stats_data,
        'squadre_popolari': squadre_popolari,
        'anni_stagione': anni_stagione,
        'titolo_pagina': "Statistiche della Tua Collezione 📈",
    }
    return render(request, 'catalogo/statistiche.html', context)

# --------------------------
# 8. Registrazione
# --------------------------
def register_user(request):
    if request.user.is_authenticated:
        return redirect('dashboard')
        
    if request.method == 'POST':
        form = RegisterForm(request.POST) 
        if form.is_valid():
            form.save()
            messages.success(request, "Account creato con successo! Ora puoi accedere.")
            return redirect('login') 
    else:
        form = RegisterForm()
        
    return render(request, 'catalogo/register.html', {'form': form, 'titolo_pagina': "Registrazione"})