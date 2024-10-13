#Importing Modules
import pygame
import sys
import pandas as pd
import heapq
import random
import joblib as jb
import math
import networkx as nx
import numpy as np
import copy

pygame.init()

#Setting up the screen
SCREEN_WIDTH = 1600
SCREEN_HEIGHT = 900
screen = pygame.display.set_mode((SCREEN_WIDTH, SCREEN_HEIGHT))
pygame.display.set_caption("Algorithm Simulation")

clock = pygame.time.Clock()

# Load port data

new_data = pd.read_csv('data_mk.csv')
new_ports_data = new_data[["Port","Berth","Quay Length (m)","Area (ha)","Max Depth (m)","Quay Cranes","Capacity (‘000 TEUs)","Country","Congestion"]]

adjacency_matrix = pd.read_csv('adjacency_matrix.csv')
locations = adjacency_matrix.index
adjacency_matrix_headless = adjacency_matrix.drop(adjacency_matrix.columns[0], axis=1)
matrix_values = adjacency_matrix_headless.values

def haversine(coord1, coord2):
    R = 6371  # Radius of the Earth in kilometers
    lat1, lon1 = coord1
    lat2, lon2 = coord2
    dlat = math.radians(lat2 - lat1)
    dlon = math.radians(lon2 - lon1)
    a = math.sin(dlat / 2) ** 2 + math.cos(math.radians(lat1)) * math.cos(math.radians(lat2)) * math.sin(dlon / 2) ** 2
    c = 2 * math.atan2(math.sqrt(a), math.sqrt(1 - a))
    distance = R * c
    return distance

G = nx.Graph()

port_locations = {
    'Singapore': (1.290270, 103.851959),
    'Vietnam': (14.058324, 108.277199),
    'Turkey': (38.963745, 35.243322),
    'China': (35.861660, 104.195397),
    'India': (20.593684, 78.962880),
    'CapeTown': (-33.918861, 18.424055),
    'SuezCanal': (30.585164, 32.559899)
}

for port1 in port_locations:
    G.add_node(port1, pos=port_locations[port1])
    for port2 in port_locations:
        if port1 != port2:
            coord1 = port_locations[port1]
            coord2 = port_locations[port2]
            distance = haversine(coord1, coord2)
            G.add_edge(port1, port2, weight=distance)

all_weights = [d['weight'] for u, v, d in G.edges(data=True)]
min_weight = min(all_weights)
max_weight = max(all_weights)

for u, v, d in G.edges(data=True):
    d['weight'] = 100 * (d['weight'] - min_weight) / (max_weight - min_weight)

port_data = pd.read_csv('Aggregated_Ports_By_Country.csv')

country_ports = {}

for _, row in port_data.iterrows():
    if row['Country'] in port_locations:
        if row['Country'] == 'SuezCanal' or row['Country'] == 'CapeTown':
            country_ports[row['Country']] = {
                'Berth': 0,
                'Quay Length (m)': 0,
                'Area (ha)': 0,
                'Quay Cranes': 0,
                'Capacity (‘000 TEUs)': 0,
                'Congestion': 0,
                'Latitude': port_locations[row['Country']][0],
                'Longitude': port_locations[row['Country']][1]
            }
        else:
            country_ports[row['Country']] = {
                'Berth': row['Total_Berths'],
                'Quay Length (m)': 0,
                'Area (ha)': row['Total_Area_ha'],
                'Quay Cranes': 0,
                'Capacity (‘000 TEUs)': row['Total_Designed_Capacity_TEUs'],
                'Congestion': 0,
                'Latitude': row['Latitude'],
                'Longitude': row['Longitude']
            }

for country, data in country_ports.items():
    data['Congestion'] = random.uniform(0, 0.089)
    data['Quay Cranes'] = random.randint(21, 50)
    data['Quay Length (m)'] = random.randint(1001, 3000)
    if country in ['SuezCanal', 'CapeTown']:
        data['Berth'] = random.randint(12, 30)
        data['Capacity (‘000 TEUs)'] = random.randint(301, 1000)
        data['Area (ha)'] = random.randint(41, 100)
    if country not in ['SuezCanal', 'CapeTown']:
        data['Capacity (‘000 TEUs)'] = data['Capacity (‘000 TEUs)'] / 1000

model_path = 'logistic_regression_model.joblib'
logistic_regression_model = jb.load(model_path)

for port, data in country_ports.items():
    features = [
        data['Berth'], data['Quay Length (m)'], data['Area (ha)'], 
        data['Quay Cranes'], data['Capacity (‘000 TEUs)'], data['Congestion']
    ]
    predicted_congestion = logistic_regression_model.predict([features])[0]
    print(f"Predicted congestion for {port}: {'Congested' if predicted_congestion == 1 else 'Not Congested'}")

for u, v, d in G.edges(data=True):
    u_data = country_ports[u]
    v_data = country_ports[v]
    
    features = [
        u_data['Berth'], u_data['Quay Length (m)'], u_data['Area (ha)'], 
        u_data['Quay Cranes'], u_data['Capacity (‘000 TEUs)'], u_data['Congestion'],
        v_data['Berth'], v_data['Quay Length (m)'], v_data['Area (ha)'], 
        v_data['Quay Cranes'], v_data['Capacity (‘000 TEUs)'], v_data['Congestion']
    ]
    
    congestion_u = logistic_regression_model.predict([features[:6]])[0]
    congestion_v = logistic_regression_model.predict([features[6:]])[0]
    
    if congestion_u == 1 or congestion_v == 1:
        d['weight'] *= 20  # Increase weight by 1000%

country_sim = 2

adj_matrice = nx.to_numpy_array(G, weight='weight')
adj_matrice = np.round(adj_matrice)
adj_matrix = copy.deepcopy(adj_matrice)
#Color Constants
WHITE = (255, 255, 255)
BLACK = (0, 0, 0)
GRAY = (150, 150, 150)
BLUE = (0, 0, 255)
RED = (255, 0, 0)
GREEN=(0,255,0)

#Fonts Constants
font = pygame.font.Font(None, 74)
button_font = pygame.font.Font(None, 50)
small_font = pygame.font.Font(None, 36)

#Loading the images
world_map = pygame.image.load('PSA-Global-Network-1.png')
world_map = pygame.transform.scale(world_map, (SCREEN_WIDTH, SCREEN_HEIGHT))
simulated_map = pygame.image.load("LocationMap.png")
simulated_map = pygame.transform.scale(simulated_map, (SCREEN_WIDTH, SCREEN_HEIGHT))
data_map = pygame.image.load('Untitled.png')
data_map = pygame.transform.scale(data_map, (SCREEN_WIDTH, SCREEN_HEIGHT))

class Button:
    def __init__(self, text, x, y, width, height, color, hover_color, shape,port_info=None,action=None,):
        self.text = text
        self.rect = pygame.Rect(x, y, width, height)
        self.color = color
        self.hover_color = hover_color
        self.port_info=port_info
        self.action = action
        self.center = (x + width // 2, y + height // 2)
        self.radius = width // 2 if width == height else min(width, height) // 2
        self.shape=shape

    def draw(self, screen,font):
        mouse_pos = pygame.mouse.get_pos()
        is_hovered = self.rect.collidepoint(mouse_pos)
        if self.shape == "circle":
            pygame.draw.circle(screen, self.hover_color if is_hovered else self.color, self.center, self.radius)
        else:  # Draw rectangle
            pygame.draw.rect(screen, self.hover_color if is_hovered else self.color, self.rect)
        #if self.rect.collidepoint(mouse_pos):
        #    pygame.draw.rect(screen, self.hover_color, self.rect)
        #else:
        #    pygame.draw.rect(screen, self.color, self.rect)
        
        adjusted_font = font
        if self.shape == "circle":
            max_text_width = int(self.radius * 1.5)  # Adjust this factor to control padding
            text_surf = font.render(self.text, True, (0, 0, 0))
            while text_surf.get_width() > max_text_width:
                font_size = adjusted_font.get_height() - 1
                adjusted_font = pygame.font.Font(None, font_size)
                text_surf = adjusted_font.render(self.text, True, (0, 0, 0))
        else:
            text_surf = font.render(self.text, True, (0, 0, 0))

        # Center and draw text
        text_rect = text_surf.get_rect(center=self.center)
        screen.blit(text_surf, text_rect)
        return is_hovered
    def check_click(self, event):
        if event.type == pygame.MOUSEBUTTONUP:
            if self.rect.collidepoint(event.pos):
                if self.action:
                    self.action()
                    print("Button clicked:", self.text)
                    return True

def display_hover_info(new_port_info, x, y):
    """Display the port info at a specified position (x, y) with a rectangle border."""
    # Define the lines of text to display

    lines = [
        f"Port: {new_port_info['Port'].values},",
        f"Country: {new_port_info['Country'].values},",
        f"Congestion: {[f'{val * 100:.0f}%' for val in new_port_info['Congestion'].values]}"
    ]

    # Calculate the height of the text box based on the number of lines
    text_height = len(lines) * 20  # Assuming 20 pixels per line
    border_rect = pygame.Rect(x - 300, y - 10, 500, text_height + 20)  # Add padding to the border

    # Draw the border rectangle (black)
    pygame.draw.rect(screen, (0, 0, 0), border_rect)  # Border color
    # Draw the background rectangle (light gray)
    pygame.draw.rect(screen, (200, 200, 200), border_rect.inflate(-5, -5))  # Background color

    # Render the text and blit it to the screen
    for i, line in enumerate(lines):
        text_surface = small_font.render(line, True, (0, 0, 0))  # Black text
        screen.blit(text_surface, (x-300, y + i * 20))  # Draw each line of text

def start_game():
    global current_page
    global adj_matrix
    global adj_matrice
    adj_matrix = copy.deepcopy(adj_matrice)
    current_page = "game"

def data_game():
    global current_page
    current_page = "data"

def down_game():
    global current_page
    current_page = "down"

def next_game():
    global current_page
    current_page = "next"

def simulate_game():
    global current_page
    current_page = "simulate"

def ai_simulate():
    global current_page
    current_page = "ai"

def main_menu():
    global current_page
    current_page = "home"


def draw_labels_and_boxes(screen, small_font, input_labels, input_boxes, input_texts):
    for i, label in enumerate(input_labels):
        label_surface = small_font.render(label, True, BLACK)
        screen.blit(label_surface, (input_boxes[i].x - 300, input_boxes[i].y + 10))
        pygame.draw.rect(screen, BLACK, input_boxes[i], 2)
        text_surface = small_font.render(input_texts[i], True, BLACK)
        screen.blit(text_surface, (input_boxes[i].x + 5, input_boxes[i].y + 5))
        
def handle_input(event, active_box, input_texts):
    if event.key == pygame.K_RETURN:
        return None  # Deselect active box on 'Enter'
    elif event.key == pygame.K_BACKSPACE:
        input_texts[active_box] = input_texts[active_box][:-1]  # Remove last character
    else:
        input_texts[active_box] += event.unicode  # Add character to input text
    return active_box
    
def draw_text_with_solid_border(text, font, text_color, border_color, x, y, padding=10):
    text_surf = font.render(text, True, text_color)
    text_rect = text_surf.get_rect(center=(x, y))
    border_rect = text_rect.inflate(padding, padding)
    pygame.draw.rect(screen, border_color, border_rect)
    screen.blit(text_surf, text_rect)

def set_weight(country):
    global adj_matrix
    for i in range(len(adj_matrix)):
        for j in range(len(adj_matrix[i])):
            if(i == country or j == country) and (adj_matrix[i][j] != 0):
                adj_matrix[i][j] = 100

def set_port(country):
    global country_sim
    country_sim = country

def dijkstra(matrix,start):
    n = len(matrix)
    distances = {i: float('infinity') for i in range(n)}
    distances[start] = 0
    predecessors = {i: None for i in range(n)}
    
    priority_queue = [(0, start)]  # (distance, node)

    while priority_queue:
        current_distance, current_node = heapq.heappop(priority_queue)

        if current_distance > distances[current_node]:
            continue

        for neighbor in range(n):
            weight = matrix[current_node][neighbor]
            if weight > 0:  # If there is an edge
                distance = current_distance + weight
                if distance < distances[neighbor]:
                    distances[neighbor] = distance
                    predecessors[neighbor] = current_node
                    heapq.heappush(priority_queue, (distance, neighbor))

    return distances, predecessors

def draw_shortest_paths(screen, font, start_node):
    global adj_matrix
    distances, predecessors = dijkstra(adj_matrix, start_node)
    counter = 6
    # Iterate over the nodes to draw edges in the shortest path tree
    for node, pred in predecessors.items():
        if pred is not None:
            # Get country names and positions
            country1 = routedic[str(pred)]
            country2 = routedic[str(node)]
            pos1 = countrycoed_routes[country1]
            pos2 = countrycoed_routes[country2]
            
            # Draw the edge as a line
            pygame.draw.line(screen, (0, 255*counter/6, 0), pos1, pos2, 3)
            counter-=1  # Green color for shortest path

# Define Routes (List of waypoints for each route)
"""
route_1 = [(SCREEN_WIDTH // 2.8, 140),(400, 120),(300, 100), (100, 130), (50, 300),(70, 400), (340, 850), (600, 830),(1030,400),(SCREEN_WIDTH // 1.54,350),(SCREEN_WIDTH // 1.24 , 480)]
route_2 = [(SCREEN_WIDTH // 2.8, 140),(560,200), (600, 250), (670, 360),(1030,400),(SCREEN_WIDTH // 1.54,350),(SCREEN_WIDTH // 1.24 , 480)]
route_3 = [(SCREEN_WIDTH // 2.8, 100),(600,90),(740,70),(800,40),(1000,40),(SCREEN_WIDTH // 1.1, 210),(SCREEN_WIDTH // 1.18, 350),(1520,120)]
"""

# Define colors for the routes
route_colors = [(255, 0, 0), (0, 0, 255),(0, 255, 0)]  # Red and Blue for different routes

start_button = Button("Start", SCREEN_WIDTH // 2 - 100, 500, 200, 80, GRAY, BLUE,"rect","", start_game)
back_button = Button("Back", SCREEN_WIDTH // 2000, 0, 120, 40, GRAY, RED,"rect","", start_game)
Next_button = Button("Next", SCREEN_WIDTH // 1.08, 0, 120, 40, GRAY, GREEN,"rect","", data_game)
Previous_button = Button("Previous", SCREEN_WIDTH // 1900, 0, 150, 40, GRAY, GREEN,"rect","", data_game)
Down_button = Button("Down", SCREEN_WIDTH // 1900, 850, 150, 40, GRAY, RED,"rect","", down_game)
Simulate_button = Button("Simulate", SCREEN_WIDTH // 1900, 850, 150, 40, GRAY, BLUE,"rect","", simulate_game)
ExitSimulate_button = Button("Exit Simulation", SCREEN_WIDTH // 1400, 850, 200, 40, GRAY, BLUE,"rect","", start_game)
new_ports_data['Country'] = new_ports_data['Country'].str.strip()
ai_simulate_button = Button("AI Simulation", SCREEN_WIDTH // 2 - 100, 600, 200, 80, GRAY, BLUE, "rect", None, ai_simulate)
home_button = Button("home", SCREEN_WIDTH // 2000, 0, 120, 40, GRAY, RED, "rect", None, main_menu)
run_ai_button = Button("Run AI Simulation", SCREEN_WIDTH // 2 - 100, 750, 200, 80, GRAY, BLUE, "rect", None, ai_simulate)

countrycoed = {
    "Singapore": [SCREEN_WIDTH // 1.3, 450],
    "India": [SCREEN_WIDTH // 1.65, 320],
    "Turkey": [SCREEN_WIDTH // 3.1, 100],
    "China": [SCREEN_WIDTH // 1.14, 190],
    "Vietnam": [SCREEN_WIDTH // 1.25, 350],
    "CapeTown": [SCREEN_WIDTH // 4.25, 800],
    "SuezCanal": [SCREEN_WIDTH // 3.13, 155]
}

countrycoed_routes = {
    "Singapore": [SCREEN_WIDTH // 1.3 + 60, 450],
    "India": [SCREEN_WIDTH // 1.65 + 60, 320],
    "Turkey": [SCREEN_WIDTH // 3.1 + 60, 100],
    "China": [SCREEN_WIDTH // 1.14 + 60, 190],
    "Vietnam": [SCREEN_WIDTH // 1.25 + 60, 350],
    "CapeTown": [SCREEN_WIDTH // 4.25 + 60, 800],
    "SuezCanal": [SCREEN_WIDTH // 3.13 + 60, 155]
}

routedic = {
            '0': "Singapore",
            '1': "Vietnam",
            '2': "Turkey",
            '3': "China",
            '4': "India",
            '5': "CapeTown",
            '6': "SuezCanal"
}

port_buttons = [
    Button("Singapore", countrycoed['Singapore'][0],countrycoed['Singapore'][1], 120, 40, GRAY, BLUE, "circle", new_ports_data[new_ports_data['Country'] == 'Singapore'], data_game),
    Button("India", countrycoed['India'][0],countrycoed['India'][1], 120, 40, GRAY, BLUE, "circle", new_ports_data[new_ports_data['Country'] == 'India'], data_game),
    Button("Turkey", countrycoed['Turkey'][0],countrycoed['Turkey'][1], 120, 40, GRAY, BLUE, "circle", new_ports_data[new_ports_data['Country'] == 'Turkey'], data_game),
    Button("China", countrycoed['China'][0],countrycoed['China'][1], 120, 40, GRAY, BLUE, "circle", new_ports_data[new_ports_data['Country'] == 'China'], data_game),
    Button("Vietnam", countrycoed['Vietnam'][0],countrycoed['Vietnam'][1], 120, 40, GRAY, BLUE, "circle",new_ports_data[new_ports_data['Country'] == 'Vietnam'], data_game),
    Button("CapeTown", countrycoed['CapeTown'][0],countrycoed['CapeTown'][1], 120, 40, GRAY, BLUE, "circle",None, None),
    Button("SuezCanal", countrycoed['SuezCanal'][0],countrycoed['SuezCanal'][1], 120, 40, GRAY, BLUE, "circle",None, None),
]

def down_page():
    global current_page
    running = True

    port_buttons = [
            Button("Singapore", SCREEN_WIDTH // 2 - 100, 100, 200, 80, GRAY, RED, "rect",None, lambda: set_weight(0)),
            Button("India",SCREEN_WIDTH // 2 - 100, 200, 200, 80, GRAY, RED, "rect",None, lambda: set_weight(4)),
            Button("Turkey",SCREEN_WIDTH // 2 - 100, 300, 200, 80, GRAY, RED, "rect",None, lambda: set_weight(2)),
            Button("China", SCREEN_WIDTH // 2 - 100, 400, 200, 80, GRAY, RED, "rect",None, lambda: set_weight(3)),
            Button("Vietnam",SCREEN_WIDTH // 2 - 100, 500, 200, 80, GRAY, RED, "rect",None,lambda: set_weight(1)),
            Button("CapeTown", SCREEN_WIDTH // 2 - 100, 600, 200, 80, GRAY, RED, "rect",None, lambda: set_weight(5)),
            Button("SuezCanal",SCREEN_WIDTH // 2 - 100, 700, 200, 80,GRAY, RED, "rect",None, lambda: set_weight(6)),
        ]
    
    sim_buttons = [
        Button("Set Singapore", 100, 100, 200, 80, GRAY, RED, "rect",None, lambda: set_port(0)),
        Button("Set India", 100, 200, 200, 80, GRAY, RED, "rect",None, lambda: set_port(4)),
        Button("Set Turkey", 100, 300, 200, 80, GRAY, RED, "rect",None, lambda: set_port(2)),
        Button("Set China",  100, 400, 200, 80, GRAY, RED, "rect",None, lambda: set_port(3)),
        Button("Set Vietnam", 100, 500, 200, 80, GRAY, RED, "rect",None,lambda: set_port(1)),
    ]
    while running:
        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                running = False
            
            for button in port_buttons:
                button.check_click(event)

            Simulate_button.check_click(event)
        
        screen.blit(data_map, (0, 0))
        
        for button in port_buttons:
             button.draw(screen, button_font)
        
        for button in sim_buttons:
            button.draw(screen, button_font)

        Simulate_button.draw(screen,small_font)

        pygame.display.flip()
        clock.tick(60)
        
        if current_page == "simulate":
            simulate_page()

        
    
    pygame.quit()
    sys.exit()

def simulate_page():
    running = True
    global adj_matrix
    print(adj_matrix)

    while running:
        screen.blit(simulated_map, (0, 0))

        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                running = False

            # Check button clicks
            for button in port_buttons:
                button.check_click(event)
            ExitSimulate_button.check_click(event)
        hovered_button = None  # Reset hovered button for the frame 
        for button in port_buttons:
            # Draw each button and check for hover
            if button.draw(screen, button_font):
                hovered_button = button  # Save hovered button for displaying info

        # Draw routes

        draw_shortest_paths(screen, font, country_sim)
        """
        for route, color in zip([route_1, route_2, route_3], route_colors):
            pygame.draw.lines(screen, color, False, route, 5)  # '5' is the line thickness """
        
        ExitSimulate_button.draw(screen,small_font)

        # Display hover info if there's a hovered button with associated port_info
        if hovered_button and hovered_button.port_info is not None:  # Check if port_info is not None
            display_hover_info(hovered_button.port_info, pygame.mouse.get_pos()[0], pygame.mouse.get_pos()[1])
        
        pygame.display.flip()
        clock.tick(60)
        if current_page == "down":
            down_page()
        if current_page == "game":
            game_page()
        if current_page == "data":
            simdata_page(hovered_button.port_info)

    pygame.quit()
    sys.exit()

def game_page():
    running = True
    while running:
        screen.blit(simulated_map, (0, 0))

        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                running = False

            # Check button clicks
            for button in port_buttons:
                button.check_click(event)
            Down_button.check_click(event)

        hovered_button = None  # Reset hovered button for the frame 
        for button in port_buttons:
            # Draw each button and check for hover
            if button.draw(screen, button_font):
                hovered_button = button  # Save hovered button for displaying info

        # Draw routes

        """
        for route, color in zip([route_1, route_2, route_3], route_colors):
            pygame.draw.lines(screen, color, False, route, 5)  # '5' is the line thickness """
        
        Down_button.draw(screen,button_font)

        for i in range(len(matrix_values)):
            for j in range(len(matrix_values[i])):
                value = matrix_values[i][j]
                if(value != 0):
                    country1 = routedic[str(i)]
                    country2 = routedic[str(j)]
                    pos1 = countrycoed_routes[country1]
                    pos2 = countrycoed_routes[country2]
                    pygame.draw.line(screen, (255*value/100,255*value/100,255*value/100),pos1,pos2,3)

        # Display hover info if there's a hovered button with associated port_info
        if hovered_button and hovered_button.port_info is not None:  # Check if port_info is not None
            display_hover_info(hovered_button.port_info, pygame.mouse.get_pos()[0], pygame.mouse.get_pos()[1])

        pygame.display.flip()
        clock.tick(60)
        if current_page == "data":
            data_page(hovered_button.port_info)
        if current_page == "down":
            down_page()

    pygame.quit()
    sys.exit()
    
def simdata_page(country_data):

    running = True
    y_offset = 100  # Starting y-position for the first port's information
    current_port_index=0
    max_ports = len(country_data)
    back_button = Button("Back", SCREEN_WIDTH // 2000, 0, 120, 40, GRAY, RED,"rect","", simulate_game)
    while running:
        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                running = False
            if back_button.check_click(event)and current_port_index==0:
                simulate_page()
            elif Next_button.check_click(event):
                if current_port_index < max_ports - 1:
                    current_port_index += 1  # Increment to show the next port data
            elif Previous_button.check_click(event):
                if current_port_index > 0:
                    current_port_index -= 1  # Decrement to show the previous port data
            

        # Clear the screen and draw the data map
        screen.blit(data_map, (0, 0))

        if current_port_index < max_ports:  # Ensure index is within bounds
            row = country_data.iloc[current_port_index]  # Get the current row of data

            lines = [
                f"Port: {row['Port']}",
                f"Country: {row['Country']}",
                f"Congestion: {row['Congestion']*100:.0f}%",
                f"Berth: {row['Berth']}",
                f"Quay Length (m): {row['Quay Length (m)']}",
                f"Area (ha): {row['Area (ha)']}",
                f"Max Depth (m): {row['Max Depth (m)']}",
                f"Quay Cranes: {row['Quay Cranes']}",
                f"Capacity (‘000 TEUs): {row['Capacity (‘000 TEUs)']}"
            ]

            # Draw the current port's information
            for i, line in enumerate(lines):
                text_surface = small_font.render(line, True, BLACK)
                screen.blit(text_surface, (50, y_offset + i * 30))  # Draw each line
            # Draw the Next button only if there are more ports
            if current_port_index < max_ports - 1:
                Next_button.draw(screen, button_font)  # Draw Next button if there are more pages
            if max_ports > 1 and current_port_index > 0:
                Previous_button.draw(screen, button_font)  # Draw Previous button
            elif current_port_index==0:
                back_button.draw(screen, button_font)
        pygame.display.flip()
        clock.tick(60)

        # Return to game page if the back button is clicked



    pygame.quit()
    sys.exit()

    
def data_page(country_data):

    running = True
    y_offset = 100  # Starting y-position for the first port's information
    current_port_index=0
    max_ports = len(country_data)
    max_height = SCREEN_HEIGHT - 100  # Maximum height for content display area

    while running:
        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                running = False
            if back_button.check_click(event) and current_port_index==0:
                game_page()
            elif Next_button.check_click(event):
                if current_port_index < max_ports - 1:
                    current_port_index += 1  # Increment to show the next port data
            elif Previous_button.check_click(event):
                if current_port_index > 0:
                    current_port_index -= 1  # Decrement to show the previous port data
            

        # Clear the screen and draw the data map
        screen.blit(data_map, (0, 0))

        if current_port_index < max_ports:  # Ensure index is within bounds
            row = country_data.iloc[current_port_index]  # Get the current row of data

            lines = [
                f"Port: {row['Port']}",
                f"Country: {row['Country']}",
                f"Congestion: {row['Congestion']*100:.0f}%",
                f"Berth: {row['Berth']}",
                f"Quay Length (m): {row['Quay Length (m)']}",
                f"Area (ha): {row['Area (ha)']}",
                f"Max Depth (m): {row['Max Depth (m)']}",
                f"Quay Cranes: {row['Quay Cranes']}",
                f"Capacity (‘000 TEUs): {row['Capacity (‘000 TEUs)']}"
            ]

            # Draw the current port's information
            for i, line in enumerate(lines):
                text_surface = small_font.render(line, True, BLACK)
                screen.blit(text_surface, (50, y_offset + i * 30))  # Draw each line
            # Draw the Next button only if there are more ports
            if current_port_index < max_ports - 1:
                Next_button.draw(screen, button_font)  # Draw Next button if there are more pages
            if max_ports > 1 and current_port_index > 0:
                Previous_button.draw(screen, button_font)  # Draw Previous button
            elif current_port_index==0:
                back_button.draw(screen, button_font)
        pygame.display.flip()
        clock.tick(60)

        # Return to game page if the back button is clicked



    pygame.quit()
    sys.exit()


def ai_simulation_page():
    running = True
    input_labels = ["Berth:", "Quay Length (m):", "Area (ha):", "Quay Cranes:", "Capacity (‘000 TEUs):", "Congestion:"]
    input_boxes = [pygame.Rect(450, 140 + i * 100, 300, 40) for i in range(6)]
    input_texts = [""] * 6
    active_box = None

    while running:
        screen.fill(WHITE)  # Clear screen with white background
        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                running = False
            elif home_button.check_click(event):
                main_menu()
            elif event.type == pygame.MOUSEBUTTONDOWN:
                for i, box in enumerate(input_boxes):
                    if box.collidepoint(event.pos):
                        active_box = i
                        break
                else:
                    active_box = None
            elif event.type == pygame.KEYDOWN and active_box is not None:
                active_box = handle_input(event, active_box, input_texts)
            elif run_ai_button.check_click(event):
                if all(input_texts):
                    input_values = [float(text) if text else 0 for text in input_texts]
                    predicted_congestion = logistic_regression_model.predict([input_values])[0]
                    result_text = "Predicted congestion: Congested" if predicted_congestion == 1 else "Predicted congestion: Not Congested"
                    result_surface = small_font.render(result_text, True, BLACK)
                    screen.blit(result_surface, (SCREEN_WIDTH - result_surface.get_width() - 20, SCREEN_HEIGHT // 2))
                    persistent_result_text = result_text
                else:
                    error_text = "Please fill in all input fields."
                    error_surface = small_font.render(error_text, True, RED)
                    screen.blit(error_surface, (SCREEN_WIDTH // 2 - error_surface.get_width() // 2, SCREEN_HEIGHT // 2))
                    persistent_result_text = error_text

        if 'persistent_result_text' in locals():
            result_surface = small_font.render(persistent_result_text, True, BLACK)
            screen.blit(result_surface, (SCREEN_WIDTH - result_surface.get_width() - 20, SCREEN_HEIGHT // 2))

        home_button.draw(screen, button_font)
        run_ai_button.draw(screen, button_font)
        
        instruction_text = "Enter only integers or decimals, no text"
        instruction_surface = small_font.render(instruction_text, True, RED)
        screen.blit(instruction_surface, (SCREEN_WIDTH // 2 - instruction_surface.get_width() // 2, 50))
        draw_labels_and_boxes(screen, small_font, input_labels, input_boxes, input_texts)

        pygame.display.flip()
        clock.tick(60)

    pygame.quit()
    sys.exit()


def main_menu():
    global current_page
    running = True
    while running:
        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                running = False
            start_button.check_click(event)
            ai_simulate_button.check_click(event)
        
        screen.blit(world_map, (0, 0))
        draw_text_with_solid_border("Main Menu", font, BLACK, GRAY, SCREEN_WIDTH // 2, 100)
        start_button.draw(screen,button_font)
        ai_simulate_button.draw(screen, small_font)
        draw_text_with_solid_border("Ming Kai", small_font, BLACK, GRAY, SCREEN_WIDTH // 2, 700)
        draw_text_with_solid_border("Wei Hao", small_font, BLACK, GRAY, SCREEN_WIDTH // 2, 740)
        draw_text_with_solid_border("Chris", small_font, BLACK, GRAY, SCREEN_WIDTH // 2, 780)

        pygame.display.flip()
        clock.tick(60)
        
        if current_page == "game":
            game_page()
        if current_page == "ai":
            ai_simulation_page()

        
    
    pygame.quit()
    sys.exit()

if __name__ == "__main__":
    current_page = "menu"
    main_menu()
