import requests
import urllib.parse
import polyline
import folium
import os
import webbrowser

# ANSII COLORS 
RESET = "\033[0m"
RED = "\033[91m"
GREEN = "\033[92m"
YELLOW = "\033[93m"
BLUE = "\033[94m"
CYAN = "\033[96m"
BOLD = "\033[1m"

# API ROUTE URL AND KEY
route_url = "https://graphhopper.com/api/1/route?" 
key = "ac6d5721-c184-4e80-b0de-63937807d098"

# Users & preferences
users = {}
unit_preferences = {}  # stores "metric" or "imperial" per user

current_user = None  # track who is logged in


# ──────────────────────────────────────────────
#  UNIT HELPERS
# ──────────────────────────────────────────────

def format_distance(meters, unit):
    """Return a formatted distance string based on unit preference."""
    if unit == "imperial":
        miles = meters / 1000 / 1.60934
        return f"{miles:.1f} miles"
    else:
        km = meters / 1000
        return f"{km:.1f} km"

def format_speed(mps, unit):
    """Convert meters-per-second to a labelled speed string."""
    if unit == "imperial":
        mph = mps * 2.23694
        return f"{mph:.1f} mph"
    else:
        kmh = mps * 3.6
        return f"{kmh:.1f} km/h"

def format_duration(ms):
    """Format milliseconds as HH:MM:SS."""
    sec = int(ms / 1000 % 60)
    minute = int(ms / 1000 / 60 % 60)
    hr  = int(ms / 1000 / 60 / 60)
    return f"{hr:02d}:{minute:02d}:{sec:02d}"


# ──────────────────────────────────────────────
#  UNIT PREFERENCE SELECTION
# ──────────────────────────────────────────────

def select_unit_preference(username):
    """Prompt the user to choose a unit system and save it."""
    print(BLUE + BOLD + "╔════════════════════════════════════════════════╗")
    print("║   📏 UNIT PREFERENCE                           ║")
    print("╚════════════════════════════════════════════════╝" + RESET)
    print(YELLOW + BOLD + "Choose your preferred unit system:" + RESET)
    print("1. Metric   (km, km/h)")
    print("2. Imperial (miles, mph)")

    while True:
        choice = input("Enter 1 or 2: ").strip()
        if choice == "1":
            unit_preferences[username] = "metric"
            print(GREEN + "Unit preference set to Metric (km)." + RESET)
            break
        elif choice == "2":
            unit_preferences[username] = "imperial"
            print(GREEN + "Unit preference set to Imperial (miles)." + RESET)
            break
        else:
            print(RED + "Invalid choice. Please enter 1 or 2." + RESET)


def get_unit(username):
    """Return the stored unit preference for a user, defaulting to metric."""
    return unit_preferences.get(username, "metric")


# ──────────────────────────────────────────────
#  MAP GENERATION
# ──────────────────────────────────────────────

def generate_map(orig, dest, paths_data, unit="metric"):
    start_coords = (orig[1], orig[2])
    dest_coords  = (dest[1], dest[2])
    route_map = folium.Map(location=start_coords, zoom_start=17, control_scale=True)

    encoded_polyline  = paths_data["paths"][0]["points"]
    decoded_coordinates = polyline.decode(encoded_polyline)

    folium.PolyLine(
        locations=decoded_coordinates,
        color="#3388ff",
        weight=6,
        opacity=0.8,
        tooltip="Route Path"
    ).add_to(route_map)

    folium.Marker(
        start_coords,
        popup=f"<b>Start:</b> {orig[3]}",
        icon=folium.Icon(color='green', icon='play')
    ).add_to(route_map)

    folium.Marker(
        dest_coords,
        popup=f"<b>End:</b> {dest[3]}",
        icon=folium.Icon(color='red', icon='stop')
    ).add_to(route_map)

    # Distance label respects unit preference
    dist_label = format_distance(paths_data["paths"][0]["distance"], unit)
    unit_label = "Imperial" if unit == "imperial" else "Metric"

    title_html = f'''
        <div style="position: fixed; 
                    bottom: 50px; left: 50px; width: 260px; height: 120px; 
                    background-color: white; border:2px solid grey; z-index:9999; font-size:14px;
                    border-radius: 10px; padding: 10px;">
        <b>Navigation Summary</b><br>
        From: {orig[3][:22]}...<br>
        To: {dest[3][:22]}...<br>
        Distance: {dist_label}<br>
        <span style="font-size:11px; color:grey;">Units: {unit_label}</span>
        </div>
    '''
    route_map.get_root().html.add_child(folium.Element(title_html))

    map_file = "navigation_ui.html"
    route_map.save(map_file)
    print("╔══════════════════════════════════════════════════════════╗")
    print("║" + GREEN + f" Visual UI saved to: {os.path.abspath(map_file)}" + RESET + " ║")
    print("╚══════════════════════════════════════════════════════════╝")
    webbrowser.open('file://' + os.path.realpath(map_file))


# ──────────────────────────────────────────────
#  AUTH
# ──────────────────────────────────────────────

def login():
    global current_user
    print(BLUE + BOLD + "╔════════════════════════════════════════════════╗")
    print("║   🔵 LOGIN PAGE                                ║")
    print("╚════════════════════════════════════════════════╝" + RESET)
    print(YELLOW + BOLD + "Login to your account" + RESET)
    username = input("Username: ")
    password = input("Password: ")

    if username in users and users[username] == password:
        current_user = username
        print(GREEN + "Login successful!" + RESET)

        # Ask to update units or keep existing preference
        if username in unit_preferences:
            current = unit_preferences[username].capitalize()
            print(CYAN + f"Current unit preference: {current}" + RESET)
            change = input("Change unit preference? (y/n): ").strip().lower()
            if change == "y":
                select_unit_preference(username)
        else:
            select_unit_preference(username)

        welcome()
        return True
    elif username not in users:
        print(RED + "Username does not exist. Please create an account." + RESET)
        return False
    else:
        print(RED + "Invalid username or password. Please try again." + RESET)
        return False


def register():
    global current_user
    print(BLUE + BOLD + "╔════════════════════════════════════════════════╗")
    print("║   🔵 REGISTER PAGE                             ║")
    print("╚════════════════════════════════════════════════╝" + RESET)
    print(YELLOW + BOLD + "Create a new account" + RESET)
    new_username = input("New Username: ")
    new_password = input("New Password: ")

    if new_username == "" or new_password == "":
        print(RED + "Username and password cannot be empty. Please try again." + RESET)
    elif new_username in users:
        print(RED + "Username already exists. Please choose a different username." + RESET)
    else:
        users[new_username] = new_password
        print(GREEN + "Account created successfully!" + RESET)
        current_user = new_username
        select_unit_preference(new_username)
        login()


# ──────────────────────────────────────────────
#  GEOCODING
# ──────────────────────────────────────────────

def geocoding(location, key):
    while location == "":
        location = input("Enter location again: ")

    geocode_url = "https://graphhopper.com/api/1/geocode?"
    url = geocode_url + urllib.parse.urlencode({"q": location, "limit": "1", "key": key})

    replydata  = requests.get(url)
    json_data  = replydata.json()
    json_status = replydata.status_code

    if json_status == 200 and len(json_data["hits"]) != 0:
        json_data = requests.get(url).json()
        lat   = json_data["hits"][0]["point"]["lat"]
        lng   = json_data["hits"][0]["point"]["lng"]
        name  = json_data["hits"][0]["name"]
        value = json_data["hits"][0]["osm_value"]

        country = json_data["hits"][0].get("country", "")
        state   = json_data["hits"][0].get("state", "")

        if len(state) != 0 and len(country) != 0:
            new_loc = name + ", " + state + ", " + country
        elif len(country) != 0:
            new_loc = name + ", " + country
        else:
            new_loc = name

        print(YELLOW + BOLD + "Geocoding API URL for " + RESET + new_loc +
              " (Location Type: " + value + ")\n" + url)
    else:
        lat = "null"
        lng = "null"
        new_loc = location
        if json_status != 200:
            print("Geo API Status: " + str(json_status) +
                  "\nError message: " + json_data["message"])

    return json_status, lat, lng, new_loc


# ──────────────────────────────────────────────
#  WELCOME
# ──────────────────────────────────────────────

def welcome():
    print("╔════════════════════════════════════════════════╗")
    print("║" + GREEN + "     Welcome to the Command Navigation Tool!    " + RESET + "║")
    print("╚════════════════════════════════════════════════╝")
    print(YELLOW + BOLD + "Choose command below" + RESET)
    print("1. Navigate Directions")
    print("2. Change Unit Preference")
    print("3. Exit")
    command = input("Enter command number: ")

    if command == "1":
        main()
    elif command == "2":
        select_unit_preference(current_user)
        welcome()
    elif command == "3" or command.lower() in ("exit", "quit"):
        print(GREEN + "Exiting the program. Goodbye!" + RESET)
        exit()
    else:
        print(RED + "Invalid command. Please try again." + RESET)
        welcome()


# ──────────────────────────────────────────────
#  MAIN NAVIGATION
# ──────────────────────────────────────────────

def main():
    unit = get_unit(current_user)
    unit_label = "Imperial (miles/mph)" if unit == "imperial" else "Metric (km/km/h)"

    while True:
        print("╔══════════════════════════════════════════════════════════╗")
        print("║" + GREEN + "      Vehicle profiles available on Graphhopper" + RESET + "           ║")
        print("║" + GREEN + "                  Car, Bike, Foot" + RESET + "                         ║")
        print("║" + CYAN  + f"      Active units: {unit_label:<38}" + RESET + "║")
        print("╚══════════════════════════════════════════════════════════╝")

        profile = ["car", "bike", "foot"]
        vehicle = input(YELLOW + BOLD +
                        "Enter a vehicle profile (Q or q to exit): " +
                        RESET).lower().strip()

        if vehicle in ("quit", "q"):
            break
        elif vehicle not in profile:
            vehicle = "car"
            print(RED + "No valid vehicle profile entered. Using car." + RESET)

        loc1 = input("Starting Location: ")
        if loc1.lower() in ("q", "quit"):
            break
        orig = geocoding(loc1, key)

        loc2 = input("Destination: ")
        if loc2.lower() in ("q", "quit"):
            break
        dest = geocoding(loc2, key)

        print("╔══════════════════════════════════════════════════════════╗")

        if orig[0] == 200 and dest[0] == 200:
            op = "&point=" + str(orig[1]) + "%2C" + str(orig[2])
            dp = "&point=" + str(dest[1]) + "%2C" + str(dest[2])
            paths_url    = route_url + urllib.parse.urlencode({"key": key, "vehicle": vehicle}) + op + dp
            paths_status = requests.get(paths_url).status_code
            paths_data   = requests.get(paths_url).json()

            print("║ " + YELLOW + BOLD + "Routing API Status: " + RESET + GREEN + str(paths_status) + RESET)
            print("║ " + YELLOW + BOLD + "Routing API URL: "    + RESET + GREEN + paths_url + RESET)
            print("╚══════════════════════════════════════════════════════════╝")

            print("╔══════════════════════════════════════════════════════════╗")
            print(f"║ Directions from {orig[3]} to {dest[3]} by {vehicle}")
            print("╚══════════════════════════════════════════════════════════╝")

            if paths_status == 200:
                total_dist_m  = paths_data["paths"][0]["distance"]
                total_time_ms = paths_data["paths"][0]["time"]

                dist_str = format_distance(total_dist_m, unit)
                time_str = format_duration(total_time_ms)

                # Average speed
                avg_mps  = (total_dist_m / (total_time_ms / 1000)) if total_time_ms > 0 else 0
                speed_str = format_speed(avg_mps, unit)

                print("╔══════════════════════════════════════════════════════════╗")
                print(f"║ Distance Traveled : {dist_str}")
                print(f"║ Trip Duration     : {time_str}")
                print(f"║ Average Speed     : {speed_str}")
                print(f"║ Units             : {unit_label}")
                print("╚══════════════════════════════════════════════════════════╝")

                for each in range(len(paths_data["paths"][0]["instructions"])):
                    path     = paths_data["paths"][0]["instructions"][each]["text"]
                    distance = paths_data["paths"][0]["instructions"][each]["distance"]
                    dist_step = format_distance(distance, unit)
                    print("╔══════════════════════════════════════════════════════════╗")
                    print(f"║ {path} ( {dist_step} )")
                    print("╚══════════════════════════════════════════════════════════╝")

                generate_map(orig, dest, paths_data, unit=unit)

            else:
                print("║ Error message: " + paths_data["message"])
                print("╚══════════════════════════════════════════════════════════╝")


# ──────────────────────────────────────────────
#  DEVELOPERS
# ──────────────────────────────────────────────

def developers():
    print(BLUE + BOLD + "╔════════════════════════════════════════════════╗")
    print("║   🔵 DEVELOPERS                                ║" + RESET)
    print(BLUE + BOLD + "║" + RESET + YELLOW + BOLD + "     This project was developed by              " + RESET + BLUE + BOLD + "║" + RESET)
    devs = [
        "1. John Kyle Boyonas",
        "2. Harby Glen Aguilar",
        "3. Jemar Celoso",
        "4. Francis Tanga-an",
        "5. John Dominic Seraspe",
        "6. Keane Gabriel Juario",
    ]
    for d in devs:
        print(BLUE + BOLD + "║" + RESET + GREEN + f"     {d:<42}" + RESET + BLUE + BOLD + "║" + RESET)
    print(BLUE + BOLD + "╚════════════════════════════════════════════════╝" + RESET)


# ──────────────────────────────────────────────
#  MAIN INTERFACE
# ──────────────────────────────────────────────

while True:
    print(BLUE + BOLD + "╔════════════════════════════════════════════════╗")
    print("║   🔵 Destination Navigation Tool v9.0          ║")
    print("║   A Navigational Tool using Graphhopper API    ║")
    print("╚════════════════════════════════════════════════╝" + RESET)
    print(YELLOW + BOLD + "Choose command below" + RESET)
    print("1. Login")
    print("2. Create Account")
    print("3. Developers")
    print("4. View Account Counts")
    print("5. Exit")
    command = input("Enter command number: ")

    if command == "1":
        if login():
            welcome()
    elif command == "2":
        register()
    elif command == "3":
        developers()
    elif command == "4":
        print(GREEN + f"Total registered accounts: {len(users)}" + RESET)
    elif command == "5" or command.lower() in ("exit", "quit"):
        print(GREEN + "Exiting the program. Goodbye!" + RESET)
        exit()
    else:
        print(RED + "Invalid command. Please try again." + RESET)