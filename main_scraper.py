from jina_web_scraper import get_latest_ads_content
from extract_with_gen_ai import extract_with_ai
from decision import verifier_opportunite


# --- BOUCLE PRINCIPALE ---
data = get_latest_ads_content("Nantes", "50")

for ad in data:
    # 1. L'IA extrait les données proprement
    # On passe le raw_text (Jina) à l'IA
    info_ia = extract_with_ai(ad['raw_text'])
    
    if info_ia:
        # 2. On calcule le prix au m2 avec les chiffres de l'IA
        p = info_ia.get('prix')
        s = info_ia.get('surface')
        
        if p and s:
            prix_m2_annonce = p / s
            
            # On prépare l'objet pour la comparaison
            annonce_propre = {
                "url": ad['url'],
                "lieu": info_ia.get('ville', 'Inconnu'),
                "type": info_ia.get('type_bien', 'Inconnu'),
                "prix_m2": prix_m2_annonce
            }
            
            # 3. Comparaison avec la (fausse) base Mongo
            verdict = verifier_opportunite(annonce_propre)
            
            # 4. Affichage du résultat final
            print(f"🏠 Bien : {annonce_propre['type']} à {annonce_propre['lieu']}")
            print(f"💰 Prix IA : {p}€ pour {s}m2 ({prix_m2_annonce:.2f}€/m2)")
            print(f"📊 Verdict : {verdict['verdict']} (Ecart : {verdict['ecart']})")
            print("-" * 40)
            