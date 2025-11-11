import math

def haversine_distance(lat1: float, lon1: float, lat2: float, lon2: float) -> float:
    """Calcula la distancia en kilómetros entre dos puntos en la Tierra usando la fórmula de Haversine."""
    R = 6371.0  # Radio de la Tierra en km

    lat1_rad = math.radians(lat1)
    lon1_rad = math.radians(lon1)
    lat2_rad = math.radians(lat2)
    lon2_rad = math.radians(lon2)

    dlon = lon2_rad - lon1_rad
    dlat = lat2_rad - lat1_rad

    a = math.sin(dlat / 2)**2 + math.cos(lat1_rad) * math.cos(lat2_rad) * math.sin(dlon / 2)**2
    c = 2 * math.asin(math.sqrt(a))

    return R * c

def euclidean_distance(lat1: float, lon1: float, lat2: float, lon2: float) -> float:
    """Calcula una distancia euclidiana aproximada en kilómetros."""
    # 1 grado ≈ 111 km (aproximación para latitudes similares)
    return math.sqrt((lat2 - lat1)**2 + (lon2 - lon1)**2) * 111.0