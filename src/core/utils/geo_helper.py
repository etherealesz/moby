import math

import numpy as np

EARTH_RADIUS_METER = 6_371_000.0


def haversine_distance(lat1: float, lon1: float, lat2: float, lon2: float) -> float:
    phi1 = math.radians(lat1)
    phi2 = math.radians(lat2)
    delta_phi = math.radians(lat2 - lat1)
    delta_lambda = math.radians(lon2 - lon1)

    a = (
        math.sin(delta_phi / 2.0) ** 2
        + math.cos(phi1) * math.cos(phi2) * math.sin(delta_lambda / 2.0) ** 2
    )
    return 2.0 * EARTH_RADIUS_METER * math.asin(math.sqrt(min(1.0, a)))


def haversine_distances(
    lat: float,
    lon: float,
    lats: np.ndarray,
    lons: np.ndarray,
) -> np.ndarray:
    phi1 = np.radians(lat)
    phi2 = np.radians(lats)
    delta_phi = phi2 - phi1
    delta_lambda = np.radians(lons - lon)

    a = (
        np.sin(delta_phi / 2.0) ** 2
        + np.cos(phi1) * np.cos(phi2) * np.sin(delta_lambda / 2.0) ** 2
    )
    return 2.0 * EARTH_RADIUS_METER * np.arcsin(np.sqrt(np.minimum(1.0, a)))
