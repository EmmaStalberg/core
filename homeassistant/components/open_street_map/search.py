"""Module to search for addresses or coordinates using the OpenStreetMap API."""

import requests
from shareLocation import generate_map_url


NOMINATIM_URL = "https://nominatim.openstreetmap.org/search"


# Search for an address using OpenStreetMap's Nominatim API
def search_address(query: str):
    """Search for addresses.

    Args:
        query (str): The address to search for.

    Returns:
        dict: A dictionary containing the search results or an error message.

    """
    params = {"q": query, "format": "json"}
    try:
        response = requests.get(NOMINATIM_URL, params=params, timeout=5)
        # response.raise_for_status()  # Raise HTTPError for bad responses
        return response.json()  # Return parsed JSON response
    except requests.exceptions.Timeout:
        return {"error": "Request timed out"}
    except requests.exceptions.RequestException as error:
        return {"error": f"Request failed: {error}"}


def get_address_coordinates(query: str):
    """Search for an address and return its coordinates directly.

    Args:
        query (str): The address to search for.

    Returns:
        list: A list containing longitude and latitude as floats, or an error message.

    """
    json_response = search_address(query)

    if "error" in json_response:
        return {"error": json_response["error"]}

    try:
        # Get the first result's latitude and longitude
        latitude = float(json_response[0]["lat"])
        longitude = float(json_response[0]["lon"])
        map_url = generate_map_url(latitude, longitude)
    except (IndexError, KeyError, ValueError):
        return {"error": "Coordinates could not be extracted"}
    else:
        return {"latitude": latitude, "longitude": longitude, "map_url": map_url}
