import requests
import urllib.parse
import polyline # Add this to your imports
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


# Users 
users = {}


def generate_map(orig, dest, paths_data):

    start_coords = (orig[1], orig[2])
    dest_coords = (dest[1], dest[2])
    route_map = folium.Map(location = start_coords, zoom_start = 17, control_scale = True)

    encoded_polyline = paths_data["paths"][0]["points"]
    decoded_coordinates = polyline.decode(encoded_polyline)

    folium.PolyLine(
        locations=decoded_coordinates,
        color="#3388ff",
        weight=6,
        opacity=0.8,
        tooltip="Route Path"
    ).add_to(route_map)

    # 4. Add custom markers with icons
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

    
    title_html = f'''
             <div style="position: fixed; 
                         bottom: 50px; left: 50px; width: 250px; height: 100px; 
                         background-color: white; border:2px solid grey; z-index:9999; font-size:14px;
                         border-radius: 10px; padding: 10px;">
             <b>Navigation Summary</b><br>
             From: {orig[3][:20]}...<br>
             To: {dest[3][:20]}...<br>
             Distance: {paths_data["paths"][0]["distance"]/1000:.2f} km
             </div>
             '''
    route_map.get_root().html.add_child(folium.Element(title_html))

    map_file = "navigation_ui.html"
    route_map.save(map_file)
    print("╔══════════════════════════════════════════════════════════════════════════════════════════════════════════════════════════════════════════════════════════════════╗")
    print("║" +GREEN + f" Visual UI saved to: {os.path.abspath(map_file)}" + RESET + "║")
    print("╚══════════════════════════════════════════════════════════════════════════════════════════════════════════════════════════════════════════════════════════════════╝")
    webbrowser.open('file://' + os.path.realpath(map_file))

def login():
    print(BLUE + BOLD +"╔════════════════════════════════════════════════╗")
    print("║   🔵 LOGIN PAGE                                ║")
    print("╚════════════════════════════════════════════════╝" + RESET)
    print(YELLOW + BOLD + "Login to your account" + RESET)
    username = input("Username: ")
    password = input("Password: ")

    if username in users and users[username] == password:
        print(GREEN + "Login successful!" + RESET)
        welcome()
        return True
    elif username not in users:
        print(RED + "Username does not exist. Please create an account." + RESET)
        return False
    else:
        print(RED + "Invalid username or password. Please try again." + RESET)
        return False
    
def register():
    print(BLUE + BOLD +"╔════════════════════════════════════════════════╗")
    print("║   🔵 REGISTER PAGE                             ║")
    print("╚════════════════════════════════════════════════╝" + RESET)
    print(YELLOW + BOLD + "Create a new account" + RESET)
    new_username = input("New Username: ")
    new_password = input("New Password: ")

    if new_username == "" or new_password == "":
        print(RED + "Username and password cannot be empty. Please try again." + RESET)
    else:
        if new_username in users:
            print(RED + "Username already exists. Please choose a different username." + RESET)
        else:
            users[new_username] = new_password
            print(GREEN + "Account created successfully! You can now log in." + RESET)
            login()

def geocoding(location, key):

    while location == "":
        location = input("Enter location again: ")

    geocode_url = "https://graphhopper.com/api/1/geocode?"
    url = geocode_url + urllib.parse.urlencode({"q": location, "limit": "1", "key": key})

    replydata = requests.get(url)
    json_data = replydata.json()
    json_status = replydata.status_code
    
    if json_status == 200 and len(json_data["hits"]) != 0: 
        json_data = requests.get(url).json()
        lat = json_data["hits"][0]["point"]["lat"]
        lng = json_data["hits"][0]["point"]["lng"]
        name = json_data["hits"][0]["name"]
        value = json_data["hits"][0]["osm_value"]

        if "country" in json_data["hits"][0]:
            country = json_data["hits"][0]["country"]
        else:
            country = ""

        if "state" in json_data["hits"][0]:
            state = json_data["hits"][0]["state"]
        else:
            state = ""

        if len(state) != 0 and len(country) != 0:
            new_loc = name + ", " + state + ", " + country
        elif len(state) != 0:
            new_loc = name + ", " + country
        else:
            new_loc = name
        
        print(YELLOW + BOLD + "Geocoding API URL for " + RESET + new_loc + " (Location Type: "+ value +")\n" + url)
    else:
        lat = "null"
        lng = "null"
        new_loc = location
        
        if json_status != 200:
            print("Geo API Status: " + str(json_status) + "\nError message: " + json_data["message"])

    return json_status, lat, lng, new_loc

def welcome():
    print("╔════════════════════════════════════════════════╗")
    print("║" + GREEN + "     Welcome to the Command Navigation Tool!    " + RESET + "║")
    print("╚════════════════════════════════════════════════╝")
    print(YELLOW + BOLD + "Choose command below" + RESET)
    print("1. Navigate Directions")
    print("2. Exit")
    command = input("Enter command number: ")
    if command == "1":
        main()
    elif command == "2" or command.lower() == "exit" or command.lower() == "quit":
        print(GREEN + "Exiting the program. Goodbye!" + RESET)
        exit()
    else:
        print(RED + "Invalid command. Please try again." + RESET)

def main():

    while True:
        print("╔════════════════════════════════════════════════════════╗")
        print("║" + GREEN +"        Vehicle profiles available on Graphhopper" + RESET + "       ║")
        print("║" + GREEN +"                   Car, Bike, Foot" + RESET + "                      ║")
        print("╚════════════════════════════════════════════════════════╝" + RESET)
        profile=["car", "bike", "foot"]
        vehicle = input(YELLOW + BOLD + "Enter a vehicle profile from the list above (Q or q to exit): " + RESET).lower()

        if vehicle == "quit" or vehicle == "q":
            break
        elif vehicle in profile:
            vehicle = vehicle
        else:
            vehicle = "car"
            print(RED + "No valid vehicle profile was entered. Using the car profile." + RESET) 

        loc1 = input("Starting Location: ")

        if loc1 == 'q' or loc1 == 'quit':
            break
        orig = geocoding(loc1, key)
        

        loc2 = input("Destination: ")
        if loc2 == 'q' or loc2 == 'quit':
            break
        
        dest = geocoding(loc2, key)
        print("╔══════════════════════════════════════════════════════════════════════════════════════════════════════════════════════════════════════════════════════════════════╗")
        if orig[0] == 200 and dest[0] == 200:
            op = "&point="+str(orig[1])+"%2C"+str(orig[2])
            dp = "&point="+str(dest[1])+"%2C"+str(dest[2])
            paths_url = route_url + urllib.parse.urlencode({"key":key, "vehicle":vehicle}) + op + dp
            paths_status = requests.get(paths_url).status_code
            paths_data = requests.get(paths_url).json()

            print("║ " +YELLOW + BOLD + "Routing API Status: "+ RESET + GREEN + str(paths_status) + RESET)
            print("║ " +YELLOW + BOLD + "Routing API URL: " + RESET + GREEN + paths_url + RESET)
            print("╚══════════════════════════════════════════════════════════════════════════════════════════════════════════════════════════════════════════════════════════════════╝")
            print("╔══════════════════════════════════════════════════════════════════════════════════════════════════════════════════════════════════════════════════════════════════╗")
            print("║ Directions from " + orig[3] + " to " + dest[3] + " by " + vehicle)
            print("╚══════════════════════════════════════════════════════════════════════════════════════════════════════════════════════════════════════════════════════════════════╝")
            print("╔══════════════════════════════════════════════════════════════════════════════════════════════════════════════════════════════════════════════════════════════════╗")
            if paths_status == 200:
                miles = (paths_data["paths"][0]["distance"])/1000/1.61
                km = (paths_data["paths"][0]["distance"])/1000
                sec = int(paths_data["paths"][0]["time"]/1000%60)
                min = int(paths_data["paths"][0]["time"]/1000/60%60)
                hr = int(paths_data["paths"][0]["time"]/1000/60/60)

                print("║ Distance Traveled: {0:.1f} miles / {1:.1f} km".format(miles, km))
                print("║ Trip Duration: {0:02d}:{1:02d}:{2:02d}".format(hr, min, sec))
                print("╚══════════════════════════════════════════════════════════════════════════════════════════════════════════════════════════════════════════════════════════════════╝")
                for each in range(len(paths_data["paths"][0]["instructions"])):
                    path = paths_data["paths"][0]["instructions"][each]["text"]
                    distance = paths_data["paths"][0]["instructions"][each]["distance"]
                    print("╔══════════════════════════════════════════════════════════════════════════════════════════════════════════════════════════════════════════════════════════════════╗")
                    print("║ {0} ( {1:.1f} km / {2:.1f} miles )".format(path, distance/1000, distance/1000/1.61))
                    print("╚══════════════════════════════════════════════════════════════════════════════════════════════════════════════════════════════════════════════════════════════════╝")
                generate_map(orig, dest, paths_data)
            else:
                print("║ Error message: " + paths_data["message"])
                print("╚══════════════════════════════════════════════════════════════════════════════════════════════════════════════════════════════════════════════════════════════════╝")

def developers():
    print(BLUE + BOLD +"╔════════════════════════════════════════════════╗")
    print("║   🔵 DEVELOPERS                                ║"+ RESET)
    print(BLUE + BOLD +"║" + RESET + YELLOW + BOLD + "     This project was developed by " + RESET + BLUE + BOLD +"             ║" + RESET )
    print(BLUE + BOLD + "║"+ RESET +GREEN + "     1. John Kyle Boyonas" + RESET + BLUE + BOLD +"                       ║" + RESET )
    print(BLUE + BOLD + "║" +RESET + GREEN + "     2. Harby Glen Aguilar" + RESET + BLUE + BOLD +"                      ║" + RESET)
    print(BLUE + BOLD + "║" +RESET + GREEN + "     3. Jemar Celoso" + RESET + BLUE + BOLD +"                            ║" + RESET)
    print(BLUE + BOLD + "║" +RESET + GREEN + "     4. Francis Tanga-an" + RESET + BLUE + BOLD +"                        ║" + RESET)
    print(BLUE + BOLD + "║" +RESET + GREEN + "     5. John Dominic Seraspe" + RESET + BLUE + BOLD +"                    ║" + RESET)
    print(BLUE + BOLD + "║" +RESET + GREEN + "     6. Keane Gabriel Juario" + RESET + BLUE + BOLD +"                    ║" + RESET)
    print(BLUE + BOLD +"╚════════════════════════════════════════════════╝" + RESET)

# Main Interface
while True:
    print(BLUE + BOLD +"╔════════════════════════════════════════════════╗")
    print("║   🔵 Destination Navigation Tool v8.0          ║")
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
    elif command == "5" or command.lower() == "exit" or command.lower() == "quit":
        print(GREEN + "Exiting the program. Goodbye!" + RESET)
        exit()