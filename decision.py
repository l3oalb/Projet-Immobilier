import pymongo

def verifier_opportunite(annonce_scrapee):
    """
    Compare une annonce scrapée avec les tendances MongoDB.
    annonce_scrapee: dict contenant {'prix_m2', 'lieu', 'type'}
    """
    client = pymongo.MongoClient("mongodb://localhost:27017/")
    db = client["immo_db"]
    collection = db["tendances_communes"]

    # 1. On cherche la référence DVF (on prend 2024 ou la plus récente)
    # Attention : Ta commune en base est en UPPER (via ton ETL Spark)
    commune_search = annonce_scrapee['lieu'].upper()
    
    ref_dvf = collection.find_one({
        "Commune": commune_search,
        "annee": 2024 # Ou filtrer par la plus récente
    })

    if not ref_dvf:
        return f"❓ Pas de données DVF pour {commune_search}"

    prix_m2_ref = ref_dvf['prix_median']
    prix_m2_annonce = annonce_scrapee['prix_m2']
    
    # 2. Calcul de l'écart
    difference = ((prix_m2_annonce - prix_m2_ref) / prix_m2_ref) * 100

    # 3. Verdict
    if difference <= -15:
        verdict = "🔥 EXCELLENTE AFFAIRE"
    elif difference <= 0:
        verdict = "✅ BON PRIX (Sous la médiane)"
    elif difference <= 15:
        verdict = "⚖️ PRIX DE MARCHÉ"
    else:
        verdict = "❌ TROP CHER"

    return {
        "commune": commune_search,
        "prix_annonce": prix_m2_annonce,
        "prix_dvf": prix_m2_ref,
        "ecart_pourcentage": round(difference, 2),
        "verdict": verdict,
        "nb_ventes_ref": ref_dvf['nb_ventes'] # Pour savoir si la ref est solide
    }