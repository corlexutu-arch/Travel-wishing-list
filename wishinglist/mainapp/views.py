from django.shortcuts import render, redirect
from mainapp.models import DestinatieVacanta

from convertapp.procesator import proceseaza_video_si_descriere
from extractapp.genAI import extrage_date_calatorie

# Create your views here.
def homepage (request):
    if request.method == "POST":
        url_receptionat = request.POST.get("link_input")
        
        if url_receptionat:
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
    return render(request, "mainapp/thelist.html", {"destinatii": toate_destinatiile})
