import requests
from typing import Optional, Tuple


def get_coordinates(address: str) -> Optional[Tuple[float, float]]:
    """
    Récupère les coordonnées (latitude, longitude) d'une adresse.

    Args:
        address: Adresse à géocoder

    Returns:
        Tuple (latitude, longitude) ou None si l'adresse n'est pas trouvée
    """
    url = "https://data.geopf.fr/geocodage/search"
    params = {"q": address, "limit": 1}

    try:
        response = requests.get(url, params=params)
        response.raise_for_status()
        data = response.json()

        if data.get("features"):
            coordinates = data["features"][0]["geometry"]["coordinates"]
            # API retourne [longitude, latitude]
            return (coordinates[1], coordinates[0])

        return None

    except Exception:
        return None
