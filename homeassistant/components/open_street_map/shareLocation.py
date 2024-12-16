"""Functionality to return a url link."""


# Generate an OpenStreetMap URL centered on given coordinates
def generate_map_url(lat: float, lon: float) -> str:
    """Generate a URL for OpenStreetMap centered on the given coordinates.

    Args:
        lat (float): Latitude of the location.
        lon (float): Longitude of the location.s

    Returns:
        str: The OpenStreetMap URL.

    """
    return f"https://www.openstreetmap.org/#map=16/{lat}/{lon}&layers=N"
