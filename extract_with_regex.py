import re


def extract_with_regex(text):
    text_lower = text.lower()
    
    # PRIX : On cherche un nombre suivi de € (gère les espaces et points : 311 900, 311.900)
    # On utilise \d[\d\s\.]* pour capturer les chiffres avec séparateurs
    prix_match = re.search(r'([\d\s\.\,]{3,})\s?€', text)
    
    # SURFACE : Cherche un nombre avant m2 ou m²
    surface_match = re.search(r'(\d{1,4})\s?m[²2]', text)
    
    # Nettoyage des chiffres
    p = int(re.sub(r'[^\d]', '', prix_match.group(1))) if prix_match else None
    s = int(surface_match.group(1)) if surface_match else None
    
    # TYPE DE BIEN
    type_bien = "Inconnu"
    if any(word in text_lower for word in ["maison", "villa", "pavillon", "maisonvilla"]):
        type_bien = "Maison"
    elif any(word in text_lower for word in ["appartement", "duplex", "studio", "t1", "t2", "t3"]):
        type_bien = "Appartement"
    elif "garage" in text_lower or "parking" in text_lower:
        type_bien = "Garage"

    # LOCALISATION (Améliorée)
    # On cherche un code postal 5 chiffres (souvent présent dans les annonces)
    cp_match = re.search(r'\b(44\d{3})\b', text) # Ici 44 pour Nantes/Loire-Atlantique
    code_postal = cp_match.group(1) if cp_match else "Non spécifié"
    
    return p, s, type_bien, code_postal

