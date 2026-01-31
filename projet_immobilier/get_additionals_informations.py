import requests
from geopy.distance import geodesic
import requests
from geopy.distance import geodesic


def get_environment_info(lat: float, lon: float, radius: int = 500) -> dict:
    """
    Enrichissement immobilier via OpenStreetMap / Overpass API.

    Indicateurs calculés :
    - distance à l'arrêt de transport le plus proche
    - nombre d'arrêts de transport dans le rayon
    - distance à la station de train la plus proche
    - nombre de commerces de proximité
    - distance au parc le plus proche
    - distance à l'école la plus proche
    - distance à la route majeure la plus proche (nuisance)
    """

    overpass_query = f"""
    [out:json];
    (
      /* Transports */
      node(around:{radius},{lat},{lon})["highway"="bus_stop"];
      node(around:{radius},{lat},{lon})["public_transport"="platform"];

      /* Gares (rayon plus large) */
      node(around:1000,{lat},{lon})["railway"="station"];

      /* Commerces */
      node(around:{radius},{lat},{lon})["shop"];

      /* Écoles */
      node(around:{radius},{lat},{lon})["amenity"="school"];

      /* Espaces verts */
      way(around:{radius},{lat},{lon})["leisure"="park"];

      /* Routes majeures */
      way(around:{radius},{lat},{lon})["highway"~"primary|secondary|trunk"];
    );
    out center;
    """

    url = "https://overpass-api.de/api/interpreter"
    response = requests.post(url, data=overpass_query)
    data = response.json()

    transport_distances = []
    station_distances = []
    commerce_count = 0
    park_distances = []
    school_distances = []
    major_road_distances = []

    for element in data["elements"]:
        tags = element.get("tags", {})

        # Récupération coordonnées
        if element["type"] == "node":
            el_lat = element["lat"]
            el_lon = element["lon"]
        else:
            el_lat = element["center"]["lat"]
            el_lon = element["center"]["lon"]

        distance = geodesic((lat, lon), (el_lat, el_lon)).meters

        # Transports
        if (
            tags.get("highway") == "bus_stop"
            or tags.get("public_transport") == "platform"
        ):
            transport_distances.append(distance)

        # Gare
        if tags.get("railway") == "station":
            station_distances.append(distance)

        # Commerces
        if "shop" in tags:
            commerce_count += 1

        # Écoles
        if tags.get("amenity") == "school":
            school_distances.append(distance)

        # Parcs
        if tags.get("leisure") == "park":
            park_distances.append(distance)

        # Routes majeures
        if tags.get("highway") in {"primary", "secondary", "trunk"}:
            major_road_distances.append(distance)

    transport_distances.sort()
    station_distances.sort()
    park_distances.sort()
    school_distances.sort()
    major_road_distances.sort()

    return {
        "transport_distance_nearest": (
            round(transport_distances[0]) if transport_distances else None
        ),
        "transport_stop_count": len(transport_distances),
        "station_distance_nearest": (
            round(station_distances[0]) if station_distances else None
        ),
        "commerce_count": commerce_count,
        "park_distance_nearest": (round(park_distances[0]) if park_distances else None),
        "school_distance_nearest": (
            round(school_distances[0]) if school_distances else None
        ),
        "major_road_distance_nearest": (
            round(major_road_distances[0]) if major_road_distances else None
        ),
    }


if __name__ == "__main__":
    print(get_environment_info(47.218371, -1.553621))
