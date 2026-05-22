from math import asin, cos, radians, sin, sqrt


def is_valid_coordinate(latitude, longitude):
    try:
        lat = float(latitude)
        lon = float(longitude)
    except (TypeError, ValueError):
        return False

    return -90 <= lat <= 90 and -180 <= lon <= 180


def haversine_km(lat1, lon1, lat2, lon2):
    if not is_valid_coordinate(lat1, lon1) or not is_valid_coordinate(lat2, lon2):
        raise ValueError("Invalid coordinates supplied for distance calculation")

    lat1, lon1, lat2, lon2 = map(float, (lat1, lon1, lat2, lon2))
    earth_radius_km = 6371

    delta_lat = radians(lat2 - lat1)
    delta_lon = radians(lon2 - lon1)
    a = (
        sin(delta_lat / 2) ** 2
        + cos(radians(lat1)) * cos(radians(lat2)) * sin(delta_lon / 2) ** 2
    )
    c = 2 * asin(sqrt(a))
    return earth_radius_km * c


def build_google_maps_directions_url(latitude, longitude):
    if not is_valid_coordinate(latitude, longitude):
        raise ValueError("Invalid coordinates supplied for map directions")

    return (
        "https://www.google.com/maps/dir/?api=1&destination="
        f"{float(latitude)},{float(longitude)}"
    )
