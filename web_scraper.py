"""Recherche la meilleure page web correspondant à une requête donnée en utilisant l'API Serper."""

import requests
import json

import requests
import json

def find_best_real_estate_ads(ville, superficie, api_key, num_to_return=3):
    url = "https://google.serper.dev/search"
    
    # Requête plus souple : on enlève les guillemets stricts sur la superficie
    search_query = f'site:leboncoin.fr OR site:pap.fr OR site:seloger.com vente {ville} {superficie} m2'
    
    payload = json.dumps({
        "q": search_query,
        "gl": "fr",
        "hl": "fr"
    })
    
    headers = {
        'X-API-KEY': api_key,
        'Content-Type': 'application/json'
    }

    try:
        response = requests.post(url, headers=headers, data=payload)
        results = response.json()
        
        if "organic" not in results:
            print("Désolé, aucun résultat organique trouvé.")
            return []

        valid_links = []
        for item in results["organic"]:
            link = item.get("link")
            
            # Simplification : On vérifie juste que c'est une URL valide et pas un PDF
            if link and not link.lower().endswith('.pdf'):
                valid_links.append({
                    "title": item.get("title"),
                    "link": link
                })
            
            if len(valid_links) >= num_to_return:
                break
            
        return valid_links

    except Exception as e:
        print(f"Erreur : {e}")
        return []


# --- CONFIGURATION ET TEST---
SERPER_API_KEY = "91ccb594ac36b2c3c487ace8729af01587a53ff9"
ma_requete = "Sustainability or ESG report Lonza pharmaceuticals 2024"

resultat = find_best_real_estate_ads("Lyon","50", SERPER_API_KEY, num_to_return=3)
print("\n--- RÉSULTAT FINAL ---")
print(f"Pages trouvées : {resultat}")