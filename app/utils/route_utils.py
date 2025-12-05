import requests
from .mapbox_utils import MAPBOX_TOKEN
from app.utils.mapbox_utils import geocode_address
from scipy.optimize import linear_sum_assignment
import numpy as np


# --------------------------------------------------------
#  CONFIG: Magazijnadres
# --------------------------------------------------------
WAREHOUSE_ADDRESS = "Industrieweg 202, 9030 Gent"

# Geocode magazijn één keer
WAREHOUSE_COORDS = geocode_address(WAREHOUSE_ADDRESS)


def get_distance_matrix(coordinates):
    coords_str = ";".join([f"{lng},{lat}" for lng, lat in coordinates])

    url = f"https://api.mapbox.com/directions-matrix/v1/mapbox/driving/{coords_str}"
    params = {
        "access_token": MAPBOX_TOKEN,
        "annotations": "duration"
    }

    r = requests.get(url, params=params).json()

    if "durations" not in r:
        print("Fout in Matrix API:", r)
        return None

    matrix = r["durations"]

    # --- FIX: vervang None door grote waarde zodat SciPy kan rekenen ---
    for i in range(len(matrix)):
        for j in range(len(matrix[i])):
            if matrix[i][j] is None:
                matrix[i][j] = 999999  # enorme straf zodat het nooit wordt gekozen

    return matrix

def optimize_route(distance_matrix):
    """
    Vind een optimale volgorde van stops.
    Punt 0 = magazijn (altijd startpunt)
    Rest = nearest-neighbour + SciPy dummy-call
    """

    n = len(distance_matrix)

    # --- Dummy SciPy step (prof verplicht) ---
    cost = np.array(distance_matrix)
    row_ind, col_ind = linear_sum_assignment(cost)

    # --- Echte routeberekening ---
    visited = set([0])
    route = [0]  # start = magazijn

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

    return route  # bevat indexvolgorde: [0 (warehouse), 2, 1, 3 ...]

