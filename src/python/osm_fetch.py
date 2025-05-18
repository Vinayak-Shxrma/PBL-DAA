import time
import requests
import mysql.connector
from db_setup import DB_CONFIG

ORS_API_KEY = "5b3ce3597851110001cf6248a6897b9815c5486798c7249699d960ca"
GEOCODE_URL = "https://api.openrouteservice.org/geocode/search"
ROUTE_URL = "https://api.openrouteservice.org/v2/directions/driving-car"

cities = ["Dehradun", "Haridwar", "Rishikesh", "Roorkee", "Mussoorie",
          "Nainital", "Haldwani", "Rudrapur", "Pantnagar", "Kashipur",
          "Ramnagar", "Almora", "Ranikhet", "Bageshwar", "Pithoragarh"]

def get_coordinates(city):
    params = {
        "api_key": ORS_API_KEY,
        "text": city,
        "boundary.country": "IN"
    }
    try:
        response = requests.get(GEOCODE_URL, params=params)
        response.raise_for_status()
        data = response.json()
        coords = data["features"][0]["geometry"]["coordinates"]
        return coords  # [lon, lat]
    except Exception:
        print(f"[Error] Failed to fetch coordinates for: {city}")
        return None

def get_distance(coord1, coord2, city1, city2):
    headers = {"Authorization": ORS_API_KEY, "Content-Type": "application/json"}
    body = {
        "coordinates": [coord1, coord2]
    }
    try:
        response = requests.post(ROUTE_URL, headers=headers, json=body)
        response.raise_for_status()
        distance_m = response.json()['routes'][0]['summary']['distance']
        return round(distance_m / 1000, 2)  # km
    except Exception:
        print(f"[Error] Failed to get distance between: {city1} ↔ {city2}")
        return None

def insert_into_db(city1, city2, distance):
    conn = mysql.connector.connect(**DB_CONFIG)
    cursor = conn.cursor()
    cursor.execute(
        "INSERT INTO highways (city1, city2, distance) VALUES (%s, %s, %s)",
        (city1, city2, distance)
    )
    conn.commit()
    conn.close()

def fetch_and_store_routes():
    coordinates = {}
    for city in cities:
        coords = get_coordinates(city)
        if coords:
            coordinates[city] = coords
        time.sleep(1)

    for i in range(len(cities)):
        for j in range(i + 1, len(cities)):
            city1 = cities[i]
            city2 = cities[j]
            if city1 in coordinates and city2 in coordinates:
                distance = get_distance(coordinates[city1], coordinates[city2], city1, city2)
                if distance:
                    print(f"Inserting route: {city1} ↔ {city2} = {distance} km")
                    insert_into_db(city1, city2, distance)
                    time.sleep(1)

if __name__ == "__main__":
    fetch_and_store_routes()
