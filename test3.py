import searoute as sr
import folium

port_locations = {
    'Singapore': (1.290270, 103.851959),
    'Vietnam': (14.058324, 108.277199),
    'Turkey': (38.963745, 35.243322),
    'China': (35.861660, 104.195397),
    'India': (20.593684, 78.962880),
    'Cape Town': (-33.918861, 18.424055),
    'Suez Canal': (30.585164, 32.559899)
}

# Define origin and destination points
origin = [port_locations['Singapore'][0], port_locations['Singapore'][1]]
destination = [port_locations['Vietnam'][0], port_locations['Vietnam'][1]]

# Change (latitude, longitude) to (longitude, latitude)
origin[0], origin[1] = origin[1], origin[0]
destination[0], destination[1] = destination[1], destination[0]

# Instantiate the route object
route = sr.searoute(origin, destination, speed_knot=12.5, units="naut")

# Obtain the route from the object
coordinates = route['geometry']['coordinates']

# Change (longitude, latitude) to (latitude, longitude) 
coordinates = [[coord[1], coord[0]] for coord in coordinates]

# Create a map object
m = folium.Map(location=coordinates[0], zoom_start=6)

# Add a marker for each coordinate
for coord in coordinates:
    folium.CircleMarker(location=coord, radius=1, fill_color='black', color='black').add_to(m)

# Create a line between coordinates
folium.PolyLine(locations=coordinates, color='black', weight=1).add_to(m)

# Save the map object as an HTML file
m.save('map.html')

# Obtain the distance and time required for passage
properties=route["properties"]