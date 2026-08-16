import os
import cv2
import easyocr
import yt_dlp

def proceseaza_video_si_descriere(url):
    """
    Primește un URL de Reel, extrage descrierea text și rulează OCR pe video 
    pentru a citi textul de pe ecran. Returnează un dicționar cu ambele texte.
    """
    # 1. Configurare yt-dlp pentru descărcare video temporar
    nume_fisier_video = "temporar_reel.mp4"
    ydl_opts = {
        'format': 'best[ext=mp4]/best',
        'outtmpl': nume_fisier_video,
        'quiet': True,
    }

    text_descriere = ""

    try:
        with yt_dlp.YoutubeDL(ydl_opts) as ydl:
            # extragere informații despre video
            info = ydl.extract_info(url, download=True)
            # extragere text din descriere 
            text_descriere = info.get('description', '')
    except Exception as e:
        print(f"Eroare la descărcare sau extragere descriere: {e}")
        text_descriere = "Nu s-a putut extrage descrierea."

    # 2. Procesare Video OCR (Citire text de pe ecran)
    text_ecran_lista = []
    
    # verificare dacă fișierul video s-a descărcat cu succes înainte de a fi deschis
    if os.path.exists(nume_fisier_video):
        try:
            # initializere cititorul EasyOCR pentru Engleză și Română
            reader = easyocr.Reader(['en', 'ro'], gpu=False) # gpu=False se asigură că rulează stabil pe procesor (CPU)
            
            # deschidere video-ul cu OpenCV
            cap = cv2.VideoCapture(nume_fisier_video)
            fps = cap.get(cv2.CAP_PROP_FPS) # numărul de cadre pe secundă
            
            if fps == 0: 
                fps = 30 # Valoare de siguranță în caz că metadatele lipsesc
                
            numar_cadru = 0
            
            while True:
                ret, frame = cap.read()
                if not ret:
                    break
                
                # citire un cadru la fiecare 1.5 secunde din video.
                if numar_cadru % int(fps * 1.5) == 0:
                    # rulare OCR pe cadrul curent
                    rezultat_ocr = reader.readtext(frame, detail=0) # detail=0 returnează doar textul curat, fără coordonate
                    if rezultat_ocr:
                        text_ecran_lista.extend(rezultat_ocr)
                
                numar_cadru += 1
                
            cap.release()
        except Exception as e:
            print(f"Eroare la procesarea OCR a video-ului: {e}")
        finally:
            # odata terminată procesarea, fișierul video se șterge
            if os.path.exists(nume_fisier_video):
                os.remove(nume_fisier_video)

    # eliminarea cuvintelor duplicat, în situația în care rămân afișate timp de mai multe cadre 
    text_ecran_unic = list(set(text_ecran_lista))
    text_ecran_final = " ".join(text_ecran_unic)

    # returnare rezultat sub formă de dicționar
    return {
        "descriere_text": text_descriere,
        "ecran_text": text_ecran_final
    }