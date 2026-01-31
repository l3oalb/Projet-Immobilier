from jina_web_scraper import get_latest_ads_content
from extract_with_gen_ai import extract_with_ai
from decision import verifier_opportunite


# --- BOUCLE PRINCIPALE ---
ads_data = get_latest_ads_content("Nantes", "50")

for ad in ads_data:
    print(f"ad content : {ad['content']}")  # DEBUG

    info_ia = extract_with_ai(ad['content'])
    
    if info_ia:
        p = info_ia.get('prix')
        s = info_ia.get('surface')
        
        if p and s:
            prix_m2_annonce = p / s
            
            annonce_propre = {
                "url": ad['url'],
                "lieu": info_ia.get('ville', 'Inconnu'),
                "type": info_ia.get('type_bien', 'Inconnu'),
                "prix_m2": prix_m2_annonce
            }
            
            # Appel de la fonction de comparaison
            resultat_comparaison = verifier_opportunite(annonce_propre)
            
            print(f"🏠 Bien : {annonce_propre['type']} à {annonce_propre['lieu']}")
            print(f"💰 Prix IA : {p}€ pour {s}m2 ({prix_m2_annonce:.2f}€/m2)")

            # Vérification si on a reçu un dictionnaire (succès) ou une string (erreur)
            if isinstance(resultat_comparaison, dict):
                print(f"📊 Verdict : {resultat_comparaison['verdict']} (Ecart : {resultat_comparaison['ecart_pourcentage']}%)")
                print(f"📍 Réf DVF ({resultat_comparaison['commune']}) : {resultat_comparaison['prix_dvf']}€/m2")
            else:
                # C'est le message "❓ Pas de données DVF"
                print(f"📊 Verdict : {resultat_comparaison}")
                
            print("-" * 40)
        else:
            print("⚠️ Informations de prix ou surface manquantes dans les données IA.")
    else:
        print("⚠️ Échec de l'extraction des données par l'IA.")