"""Module to search for routes as well as restaurants along that route."""

import requests

PROJECT_OSRM_URL = "http://router.project-osrm.org/route/v1/driving/%d,%d;%d,%d?"
OVERPASS_URL = 'https://overpass-api.de/api/interpreter?data=[out:json];node["amenity"="restaurant"](around:500,%d,%d);out;'
NOMINATIM_LOOKUP_URL = "https://nominatim.openstreetmap.org/lookup"

def fetch_route(start_coordinates : dict[str, float], end_coordinates : dict[str, float]):
    '''Find route between two coordinates.'''

    params = {"steps": "true", "geometries": "geojson", "overview": "full"}

    try:
        response = requests.get(
                (PROJECT_OSRM_URL % str(start_coordinates["lon"]), str(start_coordinates["lat"]), str(end_coordinates["lon"]), str(end_coordinates["lat"])),
                params=params,
                timeout=5
            )
        result = response.json()
    except requests.exceptions.Timeout:
        return {"error": "Request timed out"}
    except requests.exceptions.RequestException as error:
        return {"error": f"Request failed: {error}"}

    if result["routes"] and len(result["routes"])>0:
        return result["routes"][0]

    return {"error": "No route found"}

def find_restaurants_near(coordinates : dict[str, float], count : int):
    """Find restaurants near route where it is clicked."""

    try:
        response = requests.get(
                (OVERPASS_URL % coordinates["lat"], coordinates["lon"]),
                timeout=5
            )
        result = response.json()
        return get_details_restaurant(result["elements"].slice(0,count))
    except requests.exceptions.Timeout:
        return {"error": "Request timed out"}
    except requests.exceptions.RequestException as error:
        return {"error": f"Request failed: {error}"}

def get_details_restaurant(restaurants):
    """Attain extra details on the restaurants found."""

    node_ids_string = "?osm_ids="
    for restaurant in restaurants:
        node_ids_string += "N" + str(restaurant["id"])

    params = {
        "format" : "jsonv2",
        "addressdetails" : 1,
        "extratags" : 1,
        "namedetails" : 1
    }
    try:
        response = requests.get(
                (NOMINATIM_LOOKUP_URL + node_ids_string),
                params=params,
                timeout=5
            )
        return response.json()
    except requests.exceptions.Timeout:
        return {"error": "Request timed out"}
    except requests.exceptions.RequestException as error:
        return {"error": f"Request failed: {error}"}
