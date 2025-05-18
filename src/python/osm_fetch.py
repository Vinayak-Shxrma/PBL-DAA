import requests
import mysql.connector
import time
from db_setup import DB_CONFIG

ORS_API_KEY = "5b3ce3597851110001cf6248a6897b9815c5486798c7249699d960ca"
GEOCODE_URL = "https://api.openrouteservice.org/geocode/search"
ROUTE_URL = "https://api.openrouteservice.org/v2/directions/driving-car"

cities = [
    "Dehradun", "Haridwar", "Rishikesh", "Roorkee", "Mussoorie",
    "Nainital", "Haldwani", "Rudrapur", "Pantnagar", "Kashipur",
    "Ramnagar", "Almora", "Ranikhet", "Bageshwar", "Pithoragarh"
]

HEADERS = {
    "Authorization": ORS_API_KEY,
    "Accept": "application/json"
}

def get_coordinates(city, retries=3, delay=3):
    params = {
        "text": city,
        "boundary.country": "IN",
        "size": 1
    }
    for attempt in range(retries):
        try:
            response = requests.get(GEOCODE_URL, headers=HEADERS, params=params, timeout=10)
            response.raise_for_status()
            data = response.json()
            coords = data["features"][0]["geometry"]["coordinates"]
            return coords  # [lon, lat]
        except Exception as e:
            print(f"[Warning] Attempt {attempt+1} - Failed to fetch coordinates for {city}: {e}")
            time.sleep(delay)
    print(f"[Error] Could not fetch coordinates for city '{city}' after {retries} attempts.")
    return None

def get_distance(coord1, coord2, city1, city2, retries=3, delay=3):
    headers = {
        "Authorization": ORS_API_KEY,
        "Content-Type": "application/json"
    }
    body = {
        "coordinates": [coord1, coord2]
    }
    for attempt in range(retries):
        try:
            response = requests.post(ROUTE_URL, headers=headers, json=body, timeout=10)
            response.raise_for_status()
            distance_m = response.json()['routes'][0]['summary']['distance']
            return round(distance_m / 1000, 2)  # km
        except Exception as e:
            print(f"[Warning] Attempt {attempt+1} - Failed to get distance between {city1} ↔ {city2}: {e}")
            time.sleep(delay)
    print(f"[Error] Could not fetch distance between {city1} and {city2} after {retries} attempts.")
    return None

def insert_into_db(city1, city2, distance):
    try:
        conn = mysql.connector.connect(**DB_CONFIG)
        cursor = conn.cursor()
        cursor.execute(
            "INSERT INTO highways (city1, city2, distance) VALUES (%s, %s, %s)",
            (city1, city2, distance)
        )
        conn.commit()
        cursor.close()
        conn.close()
    except Exception as e:
        print(f"[Error] DB insertion failed for {city1} ↔ {city2}: {e}")

def fetch_and_store_routes():
    coordinates = {}
    for city in cities:
        coords = get_coordinates(city)
        if coords:
            coordinates[city] = coords
        else:
            print(f"Skipping city {city} due to missing coordinates.")

    for i in range(len(cities)):
        for j in range(i + 1, len(cities)):
            city1, city2 = cities[i], cities[j]
            if city1 in coordinates and city2 in coordinates:
                dist = get_distance(coordinates[city1], coordinates[city2], city1, city2)
                if dist is not None:
                    print(f"Inserting route: {city1} ↔ {city2} = {dist} km")
                    insert_into_db(city1, city2, dist)
                else:
                    print(f"Skipping insertion due to distance fetch failure: {city1} ↔ {city2}")
            else:
                print(f"Coordinates missing for {city1} or {city2}")

if __name__ == "__main__":
    fetch_and_store_routes()
