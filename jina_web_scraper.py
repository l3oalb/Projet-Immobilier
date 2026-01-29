import requests
import time
import os
from dotenv import load_dotenv

load_dotenv()
SERPER_API_KEY = os.getenv("SERPER_API_KEY")

def get_latest_ads_content(ville, superficie):
    """Récupère les annonces immobilières récentes pour une ville et une superficie données."""

    # ÉTAPE 1 : Trouver les URLs des dernières annonces via Serper
    search_url = "https://google.serper.dev/search"
    # On ajoute "moins de 24h" pour forcer les résultats récents
    query = f'vente {ville} {superficie}m2'
    
    payload = {
        "q": query,
        "tbs": "qdr:d", # FILTRE GOOGLE : Annonces publiées les dernières 24h uniquement
        "gl": "fr"
    }
    headers = {'X-API-KEY': SERPER_API_KEY, 'Content-Type': 'application/json'}
    
    response = requests.post(search_url, json=payload, headers=headers)
    results = response.json()
    
    ads_data = []

    # ÉTAPE 2 : Lire le contenu de chaque annonce avec Jina
    for item in results.get("organic", [])[:5]: # On prend les 3 premières pour tester

        ad_url = item.get("link")
        if "liste" in ad_url:
            continue # On ignore les pages de résultats, on veut des annonces individuelles
        print(f"Reading ad: {ad_url}")

        jina_reader_url = f"https://r.jina.ai/{ad_url}" # On passe par le proxy Jina Reader
        
        try:
            ad_content = requests.get(jina_reader_url, timeout=10).text
            ads_data.append({
                "url": ad_url,
                "content": ad_content
                })
            # Petit sleep pour être poli
            time.sleep(2)
        except Exception as e:
            print(f"Erreur Jina sur {ad_url}: {e}")
            
    return ads_data


# --- TEST ---
data = get_latest_ads_content("Nantes", "50")
