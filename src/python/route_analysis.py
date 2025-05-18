import mysql.connector
from src.python.db_setup import DB_CONFIG
from collections import defaultdict
import heapq

def fetch_highway_data():
    conn = mysql.connector.connect(**DB_CONFIG)
    cursor = conn.cursor()
    cursor.execute("SELECT city1, city2, distance FROM highways")
    rows = cursor.fetchall()
    conn.close()
    return rows

def build_graph(data):
    graph = defaultdict(list)
    for city1, city2, dist in data:
        graph[city1].append((city2, dist))
        graph[city2].append((city1, dist))
    return graph

def dijkstra(graph, start, end):
    queue = [(0, start, [])]
    visited = set()

    while queue:
        (cost, city, path) = heapq.heappop(queue)
        if city in visited:
            continue
        visited.add(city)
        path = path + [city]
        if city == end:
            return path, cost
        for neighbor, weight in graph[city]:
            if neighbor not in visited:
                heapq.heappush(queue, (cost + weight, neighbor, path))
    return None, float('inf')

def find_shortest_path(start, end):
    data = fetch_highway_data()
    graph = build_graph(data)
    return dijkstra(graph, start, end)
