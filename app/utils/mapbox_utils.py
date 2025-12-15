import requests

MAPBOX_TOKEN = "pk.eyJ1IjoiYmFydGJhdHNsZWVyIiwiYSI6ImNtaW5rbG8yYTBwd2cza3Nib3NvMHl4MWYifQ.2LaqFIMyfJqVMWu8daLDUw"

def geocode_address(address):
    """Convert address to (lng, lat) coordinates using Mapbox Geocoding API."""

    url = f"https://api.mapbox.com/geocoding/v5/mapbox.places/{address}.json"
    params = {
        "access_token": MAPBOX_TOKEN
    }

    try:
        response = requests.get(url, params=params, timeout=5)
        response.raise_for_status()  # check of er geen foute URL of token ofzo gegeven werd 
        r = response.json()

    except requests.exceptions.RequestException as e:
        print(f"Mapbox request failed: {e}")
        return None

    if "features" not in r or len(r["features"]) == 0:
        return None

    coords = r["features"][0]["geometry"]["coordinates"]
    lng, lat = coords[0], coords[1]

    return lng, lat
