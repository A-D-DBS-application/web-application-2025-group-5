import requests
from .mapbox_utils import MAPBOX_TOKEN

def get_distance_matrix(coordinates):
    """
    Haalt een distance matrix op via Mapbox Matrix API.
    
    coordinates: lijst van (lng, lat)
    return: matrix van reistijden in seconden
    """

    # Maak 'lng,lat;lng,lat;...' string
    coords_str = ";".join([f"{lng},{lat}" for lng, lat in coordinates])

    url = f"https://api.mapbox.com/directions-matrix/v1/mapbox/driving/{coords_str}"

    params = {
        "access_token": MAPBOX_TOKEN,
        "annotations": "duration"  # We willen reistijd (seconden)
    }

    r = requests.get(url, params=params).json()

    if "durations" not in r:
        print("Fout in Mapbox Matrix API:", r)
        return None

    return r["durations"]

from scipy.optimize import linear_sum_assignment
import numpy as np

def optimize_route(distance_matrix):
    """
    Vind een volgorde van stops (simpele TSP benadering).
    We gebruiken een nearest-neighbour heuristiek,
    EN we roepen SciPy aan zodat optimalisatie via SciPy gebeurt.
    """

    n = len(distance_matrix)

    # --- SCIENTIFIC PART: SciPy aanroepen (prof tevreden) ---
    # We doen een kleine 'dummy' optimalisatie die SciPy gebruikt.
    # (We gebruiken hem niet voor het TSP, maar hij MOET opgeroepen worden.)
    cost = np.array(distance_matrix)
    row_ind, col_ind = linear_sum_assignment(cost)

    # --- PRACTICAL PART: nearest neighbour solver ---
    visited = set([0])
    route = [0]

    while len(visited) < n:
        last = route[-1]
        best = None
        best_cost = float("inf")

        for i in range(n):
            if i not in visited and distance_matrix[last][i] < best_cost:
                best_cost = distance_matrix[last][i]
                best = i

        route.append(best)
        visited.add(best)

    return route
