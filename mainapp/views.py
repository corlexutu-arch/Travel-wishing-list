from django.shortcuts import render, redirect, get_object_or_404
from mainapp.models import DestinatieVacanta
from django.contrib import messages
from django.db.models import Q

from mainapp.services.convert import proceseaza_video_si_descriere
from mainapp.services.extract import extrage_date_calatorie

def delete_entry(request, pk):
    if request.method == 'POST':
        entry = get_object_or_404(DestinatieVacanta, pk=pk)
        entry.delete()
    return redirect('the_list')

# Create your views here.
def homepage (request):
    if request.method == "POST":
        url_receptionat = request.POST.get("link_input")
        
        if url_receptionat:
            # Check if destination already exists in the database
            if DestinatieVacanta.objects.filter(Link_original=url_receptionat).exists():
                messages.warning(request, "Destinatia deja se afla in baza de date")
                return redirect('the_list')
            
            # 1. trimitere URL către convertapp pentru descărcare și OCR
            date_brute = proceseaza_video_si_descriere(url_receptionat)
            
            # 2. trimiterea textelor extrase către extractapp pentru ca Gemini să le transforme în JSON
            json_ai = extrage_date_calatorie(
                descriere_text=date_brute["descriere_text"], 
                ecran_text=date_brute["ecran_text"]
            )
            
            # 3. salvarea cuvintelor finale în baza de date din mainapp
            DestinatieVacanta.objects.create(
                link_original=url_receptionat,
                tara=json_ai["tara"],
                locul=json_ai["locul"],
                categorie=json_ai["categorie"],
                tip_activitate=json_ai["tip_activitate"]
            )
            
            # după salvare, userul este redirecționat către pagina cu tabelul destinații
            return redirect('the_list')
    return render (request, "mainapp/home.html")

def thelist (request):
    toate_destinatiile = DestinatieVacanta.objects.all().order_by('-data_adaugarii')

    # Read search and filter parameters
    query = request.GET.get('q')
    selected_tara = request.GET.get('tara')
    selected_categorie = request.GET.get('categorie')

    # 1. Search bar filter (Țară or Activități)
    if query:
        toate_destinatiile = toate_destinatiile.filter(
            Q(tara__icontains=query) | Q(tip_activitate__icontains=query)
        )

    # 2. Country filter
    if selected_tara:
        toate_destinatiile = toate_destinatiile.filter(tara__iexact=selected_tara)

    # 3. Category filter
    if selected_categorie:
        toate_destinatiile = toate_destinatiile.filter(categorie__iexact=selected_categorie)

    # Extract unique values for the dropdowns from the database
    tari_list = DestinatieVacanta.objects.exclude(tara__isnull=True).exclude(tara='').values_list('tara', flat=True).distinct().order_by('tara')
    categorii_list = DestinatieVacanta.objects.exclude(categorie__isnull=True).exclude(categorie='').values_list('categorie', flat=True).distinct().order_by('categorie')

    context = {
        "destinatii": toate_destinatiile,
        "tari_list": tari_list,
        "categorii_list": categorii_list,
    }

    return render(request, "mainapp/thelist.html", context)