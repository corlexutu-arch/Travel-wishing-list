import json
import google.generativeai as genai
from dotenv import load_model, load_dotenv
import os


load_dotenv()

GEMINI_API_KEY = os.getenv("GEMINI_API_KEY")
genai.configure(api_key=GEMINI_API_KEY)

def extrage_date_calatorie(descriere_text, ecran_text):
    """
    Trimite textul descrierii și textul OCR de pe ecran către Gemini LLM.
    Returnează un dicționar Python (JSON) structurat pentru tabelul Django.
    """
    
    # 1. Unim cele două surse de text într-un singur context clar pentru AI
    context_complet = f"""
    --- TEXT DIN DESCRIEREA CLIPULUI (CAPTION) ---
    {descriere_text}
    
    --- TEXT CITIT DE PE ECRANUL VIDEO-ULUI (OCR) ---
    {ecran_text}
    """

    # 2. Construim instrucțiunea (Prompt-ul) cu reguli stricte de formatare în limba Română
    prompt = f"""
    Ești un asistent inteligent specializat în travel și organizarea vacanțelor.
    Analizează textele de mai jos extrase dintr-un clip video de tip Reel/Shorts despre o destinație turistică.
    
    Sarcina ta este să extragi informațiile cheie și să le returnezi EXCLUSIV sub forma unui obiect JSON valid în limba Română.
    NU adăuga text introductiv, nu adăuga explicații și NU pune blocuri de formatare markdown (cum ar fi ```json ). Returnează doar codul JSON curat.
    
    Structura strictă a obiectului JSON trebuie să fie:
    {{
        "tara": "Numele țării (ex: Vietnam, Italia, România). Dacă nu e specificată, scrie 'Nespecificată'",
        "locul": "Orașul, regiunea sau obiectivele turistice specifice menționate (separate prin virgulă dacă sunt mai multe)",
        "categorie": "Alege doar una dintre opțiuni: 'Natura', 'Urban' sau 'Mixed'",
        "tip_activitate": "Cuvinte cheie legate de ce se face acolo, separate prin virgulă (ex: hiking, plimbare, cycling, muzee, plajă, tren, restaurante)"
    }}

    Date brute din clip:
    {context_complet}
    """

    try:
        # Folosim modelul Flash, ideal pentru procesare rapidă de text și complet gratuit
        model = genai.GenerativeModel("gemini-2.5-flash")
        response = model.generate_content(prompt)
        
        # Curățăm răspunsul de eventuale spații sau caractere ciudate lăsate de LLM
        text_raspuns = response.text.strip()
        
        # Siguranță suplimentară în caz că AI-ul a ignorat instrucțiunea și a pus markdown-ul ```json
        if text_raspuns.startswith("```json"):
            text_raspuns = text_raspuns.replace("```json", "").replace("```", "").strip()
        elif text_raspuns.startswith("```"):
            text_raspuns = text_raspuns.replace("```", "").strip()

        # Transformăm textul JSON primit de la AI într-un dicționar nativ de Python
        date_structurate = json.loads(text_raspuns)
        return date_structurate

    except Exception as e:
        print(f"Eroare la parsarea sau apelul Gemini API: {e}")
        # Returnăm un fallback (valori de siguranță) ca să nu se blocheze aplicația Django
        return {
            "tara": "Eroare AI",
            "locul": "Nespecificat",
            "categorie": "Mixed",
            "tip_activitate": "eroare_procesare"
        }