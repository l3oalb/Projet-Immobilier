import requests
import time
import os
import re
from dotenv import load_dotenv

load_dotenv()
SERPER_API_KEY = os.getenv("SERPER_API_KEY")


def est_une_vraie_annonce(url):
    """ Détermine si une URL donnée ressemble à une annonce immobilière individuelle."""
    url = url.lower().strip()
    
    # 1. Élimination immédiate si ça finit par un slash (c'est une catégorie/liste)
    if url.endswith('/') or url.split('/')[-1] == "":
        return False

    # 2. On vérifie la terminaison
    # Sur Ouest-France, Figaro, ParuVendu, une annonce FINIT par .htm ou .html
    annonces_extensions = ('.htm', '.html', '.php')
    
    # Si ça ne finit pas par une extension de page ET que le dernier segment 
    # ne contient pas un ID numérique long (>5 chiffres), on rejette.
    dernier_segment = url.split('/')[-1]
    
    has_extension = url.endswith(annonces_extensions)
    has_id_in_segment = bool(re.search(r'\d{5,}', dernier_segment))

    if has_extension or has_id_in_segment:
        # On garde quand même une sécurité sur les mots clés de liste
        blacklist = ["/recherche", "/liste", "/achat", "/annuaire", "resultats"]
        if any(b in url for b in blacklist):
            return False
        return True
        
    return False


import re


def extraire_liens_annonces(html_ou_markdown):
    """
    Parcourt le contenu d'une page de liste pour trouver 
    des liens qui ressemblent à des annonces (.htm, .html avec ID).
    """
    # Regex : cherche des URLs qui finissent par .htm ou .html avec des chiffres
    patern = r'https?://[^\s"\'<>]+?\d{5,}\.html?'
    liens = re.findall(patern, html_ou_markdown)
    
    # On dédoublonne et on enlève les liens qui contiennent "recherche" ou "liste"
    liens_propres = list(set([l for l in liens if "/liste" not in l and "/recherche" not in l]))
    return liens_propres


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

    # ÉTAPE 2 : Lire le contenu de chaque annonce avec Jina
    response = requests.post(search_url, json=payload, headers=headers)
    results = response.json()
    
    all_ads_content = []

    for item in results.get("organic", []):
        url_initiale = item.get("link")
        
        # On récupère le contenu du lien Google (souvent une liste)
        jina_url = f"https://r.jina.ai/{url_initiale}"
        res = requests.get(jina_url, timeout=15)
        content = res.text

        # --- LE REBOND ---
        # Si c'est une liste, on cherche les liens d'annonces à l'intérieur
        if "résultats" in content.lower() or len(content) < 2000:
            print(f"📋 Liste détectée ({url_initiale}), extraction des liens...")
            liens_trouves = extraire_liens_annonces(content)
            
            for sub_url in liens_trouves[:5]: # On teste les 5 premières annonces de la liste
                print(f"   🔗 Rebond vers : {sub_url}")
                try:
                    res_sub = requests.get(f"https://r.jina.ai/{sub_url}", timeout=15)
                    if est_une_vraie_annonce(sub_url):
                        all_ads_content.append({"url": sub_url, "content": res_sub.text})
                        print(f"✅ Annonce ajoutée : {sub_url}")
                except:
                    print(f"❌ Échec du rebond vers {sub_url}")
                    continue
        else:
            # Si c'était déjà une annonce directe, on la prend
            all_ads_content.append({"url": url_initiale, "content": content})

        if len(all_ads_content) >= 3: break
            
    return all_ads_content


#TEST 
if __name__ == "__main__":
    ads = get_latest_ads_content("Nantes", "50")
    for ad in ads:
        print(f"URL: {ad['url']}\nContent Snippet: {ad['content'][:100]}\n{'-'*40}")
