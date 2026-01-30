import requests
import time
import os
import re
from dotenv import load_dotenv

load_dotenv()
SERPER_API_KEY = os.getenv("SERPER_API_KEY")



def get_latest_ads_content(ville, superficie):
    """Récupère les annonces immobilières récentes pour une ville et une superficie données."""

    # ÉTAPE 1 : Trouver les URLs des dernières annonces via Serper
    search_url = "https://google.serper.dev/search"
    query = f'vente {ville} {superficie}m2'
    
    payload = {
        "q": query,
        "tbs": "qdr:d", # FILTRE GOOGLE : Annonces publiées les dernières 24h uniquement
        "gl": "fr",
        "num": 10 # Nombre de résultats
    }
    headers = {'X-API-KEY': SERPER_API_KEY, 'Content-Type': 'application/json'}
    
    response = requests.post(search_url, json=payload, headers=headers)
    results = response.json()
    
    ads_data = []

    # ÉTAPE 2 : Lire le contenu de chaque annonce avec Jina
    for item in results.get("organic", [])[:5]: # On prend les 5 premières pour tester

        ad_url = item.get("link")

        if len(ads_data) >= 1: break # Limite à 1 annonce pour le test

        blacklist = ["liste", "location"] # Mots-clés à ignorer dans les URLs

        if any(b in ad_url for b in blacklist):
            continue # On ignore les pages de résultats, on veut des annonces individuelles

        jina_reader_url = f"https://r.jina.ai/{ad_url}" # On passe par le proxy Jina Reader
        
        try:
            res = requests.get(jina_reader_url, timeout=10)
            ad_content = res.text

            if not re.search(r'\d{5,}', ad_url):
                continue

            if "location" in ad_content.lower():
                continue # On ignore les pages locations

            if len(ad_content) > 500: # si le contenu est suffisamment long on ajoute
                ads_data.append({
                "url": ad_url,
                "content": ad_content
                })
                print(f"✅ Annonce trouvée : {ad_url[:100]}")

            else: # si le contenu est trop court on ignore
                print(f"⚠️ Contenu trop court pour l'URL : {ad_url[:100]}")
                time.sleep(2)
                continue
     
        except Exception as e:
            print(f"Erreur Jina : {e}")
            
    return ads_data


# --- TEST ---
if __name__ == "__main__":
    ads_data = get_latest_ads_content("Nantes", "50")
