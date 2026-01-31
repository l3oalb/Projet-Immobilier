from jina_web_scraper import get_latest_ads_content
from extract_with_gen_ai import extract_with_ai
from decision import verifier_opportunite
from get_coord_API import get_coordinates
from get_additionals_informations import get_environment_info

# --- BOUCLE PRINCIPALE ---
ads_data = get_latest_ads_content("Nantes", "50")

for ad in ads_data:
    # 1. L'IA extrait les données proprement
    # On passe le raw_text (Jina) à l'IA
    info_ia = extract_with_ai(ad["content"])

    if info_ia:
        # 2. On calcule le prix au m2 avec les chiffres de l'IA
        p = info_ia.get("prix")
        s = info_ia.get("surface")

        if p and s:
            prix_m2_annonce = p / s

            # On prépare l'objet pour la comparaison
            annonce_propre = {
                "url": ad["url"],
                "lieu": info_ia.get("ville", "Inconnu"),
                "type": info_ia.get("type_bien", "Inconnu"),
                "prix_m2": prix_m2_annonce,
            }

            # 3. Comparaison avec la (fausse) base Mongo
            verdict = verifier_opportunite(annonce_propre)

            coord = get_coordinates([annonce_propre["lieu"]])
            transport = get_environment_info(coord[0], coord[1])

            # 4. Affichage du résultat final
            print(
                f"🚌 Transport : {transport['distance_nearest']}m vers l'arrêt le plus proche"
            )
            print(
                f"Distance à l'arrêt de transport le plus proche : {transport['transport_distance_nearest']}m"
            )
            print(
                f"Nombre d'arrêts de transport dans le rayon : {transport['transport_stop_count']}"
            )
            print(
                f"Distance à la station de train la plus proche : {transport['station_distance_nearest']}m"
            )
            print(f"Nombre de commerces de proximité : {transport['commerce_count']}")
            print(
                f"Distance au parc le plus proche : {transport['park_distance_nearest']}m"
            )
            print(
                f"Distance à l'école la plus proche : {transport['school_distance_nearest']}m"
            )
            print(
                f"Distance à la route majeure la plus proche : {transport['major_road_distance_nearest']}m"
            )
            print(f"🏠 Bien : {annonce_propre['type']} à {annonce_propre['lieu']}")
            print(f"💰 Prix IA : {p}€ pour {s}m2 ({prix_m2_annonce:.2f}€/m2)")
            print(f"📊 Verdict : {verdict['verdict']} (Ecart : {verdict['ecart']})")
            print("-" * 40)
