import requests

MAPBOX_TOKEN = "pk.eyJ1IjoiYmFydGJhdHNsZWVyIiwiYSI6ImNtaW5rbG8yYTBwd2cza3Nib3NvMHl4MWYifQ.2LaqFIMyfJqVMWu8daLDUw"

def geocode_address(address):
    """Convert address to (lng, lat) coordinates using Mapbox Geocoding API."""
    
    url = f"https://api.mapbox.com/geocoding/v5/mapbox.places/{address}.json"
    
    params = {
        "access_token": MAPBOX_TOKEN
    }

    r = requests.get(url, params=params).json()

    if "features" not in r or len(r["features"]) == 0:
        return None

    coords = r["features"][0]["geometry"]["coordinates"]
    lng, lat = coords[0], coords[1]

    return lng, lat 
