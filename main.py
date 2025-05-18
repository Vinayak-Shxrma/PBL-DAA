from src.python.route_analysis import find_shortest_path

def main():
    print("Smart Route Analysis System")
    start = input("Enter start city: ").title()
    end = input("Enter destination city: ").title()

    path, distance = find_shortest_path(start, end)

    if path:
        print(f"\nShortest path from {start} to {end}: {' -> '.join(path)}")
        print(f"Total distance: {distance} km")
    else:
        print("No route found!")

if __name__ == "__main__":
    main()
