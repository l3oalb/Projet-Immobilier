import requests
import time

def get_latest_ads_content(ville, superficie, api_key_serper):
    # ÉTAPE 1 : Trouver les URLs des dernières annonces via Serper
    search_url = "https://google.serper.dev/search"
    # On ajoute "moins de 24h" pour forcer les résultats récents
    query = f'site:leboncoin.fr OR site:seloger.com vente {ville} {superficie}m2'
    
    payload = {
        "q": query,
        "tbs": "qdr:d", # FILTRE GOOGLE : Annonces publiées les dernières 24h uniquement
        "gl": "fr"
    }
    headers = {'X-API-KEY': api_key_serper, 'Content-Type': 'application/json'}
    
    response = requests.post(search_url, json=payload, headers=headers)
    results = response.json()
    
    ads_data = []

    # ÉTAPE 2 : Lire le contenu de chaque annonce avec Jina
    for item in results.get("organic", [])[:3]: # On prend les 3 premières pour tester
        ad_url = item.get("link")
        print(f"Reading ad: {ad_url}")
        
        # On passe par le proxy Jina Reader
        jina_reader_url = f"https://r.jina.ai/{ad_url}"
        
        try:
            # Jina gère les proxies et le rendu pour nous !
            ad_content = requests.get(jina_reader_url, timeout=10).text
            
            ads_data.append({
                "url": ad_url,
                "raw_text": ad_content # Ce texte contient prix, description, DPE, etc.
            })
            # Petit sleep pour être poli
            time.sleep(1)
        except Exception as e:
            print(f"Erreur Jina sur {ad_url}: {e}")
            
    return ads_data

# --- TEST ---
data = get_latest_ads_content("Nantes", "50", "VOTRE_CLE_SERPER")

if data:
    print(f"✅ {len(data)} annonce(s) récupérée(s).")
    print(f"Aperçu du texte : \n{data[0]['raw_text'][:500]}")
else:
    print("❌ Aucune donnée n'a pu être extraite. Vérifie tes quotas Serper ou ta requête.")