# Importing Modules
import pygame
import sys
import pandas as pd
import networkx as nx
import heapq

pygame.init()

# Setting up the screen
SCREEN_WIDTH = 1600
SCREEN_HEIGHT = 900
screen = pygame.display.set_mode((SCREEN_WIDTH, SCREEN_HEIGHT))
pygame.display.set_caption("Algorithm Simulation")

clock = pygame.time.Clock()

# Load port data
data = pd.read_csv('PSA_Ports_Data.csv')
ports_data = data[["PortName", "Country", "Container Berth", "Area(ha)", "Port Congestion(%)", "Designed Capacity(TEUs)", "Suez Canal Risk", "Strait of Malacca Risk", "Bab el-Mandeb Risk", "South China Sea Risk", "Indian Ocean Monsoon Risk"]]

new_data = pd.read_csv('data_mk.csv')
new_ports_data = new_data[["Port", "Berth", "Quay Length (m)", "Area (ha)", "Max Depth (m)", "Quay Cranes", "Capacity (‘000 TEUs)", "Country", "Congestion"]]

# Color Constants
WHITE = (255, 255, 255)
BLACK = (0, 0, 0)
GRAY = (150, 150, 150)
BLUE = (0, 0, 255)
RED = (255, 0, 0)
GREEN = (0, 255, 0)

# Fonts Constants
font = pygame.font.Font(None, 74)
button_font = pygame.font.Font(None, 50)
small_font = pygame.font.Font(None, 36)

# Loading the images
world_map = pygame.image.load('PSA-Global-Network-1.png')
world_map = pygame.transform.scale(world_map, (SCREEN_WIDTH, SCREEN_HEIGHT))
simulated_map = pygame.image.load("LocationMap.png")
simulated_map = pygame.transform.scale(simulated_map, (SCREEN_WIDTH, SCREEN_HEIGHT))
data_map = pygame.image.load('Untitled.png')
data_map = pygame.transform.scale(data_map, (SCREEN_WIDTH, SCREEN_HEIGHT))

# Dijkstra's Algorithm implementation
def dijkstra(graph, start_node):
    queue = [(0, start_node)]
    distances = {node: float('inf') for node in graph.nodes}
    distances[start_node] = 0
    previous_nodes = {node: None for node in graph.nodes}

    while queue:
        current_distance, current_node = heapq.heappop(queue)

        if current_distance > distances[current_node]:
            continue

        for neighbor in graph.neighbors(current_node):
            edge_weight = graph[current_node][neighbor]['weight']
            distance = current_distance + edge_weight

            if distance < distances[neighbor]:
                distances[neighbor] = distance
                previous_nodes[neighbor] = current_node
                heapq.heappush(queue, (distance, neighbor))

    return distances, previous_nodes

# Function to draw the shortest path
def draw_shortest_path(previous_nodes, start_node, end_node):
    path = []
    while end_node:
        path.append(end_node)
        end_node = previous_nodes[end_node]
    path.reverse()

    # Draw the path in red
    for i in range(len(path) - 1):
        pygame.draw.line(screen, RED, positions[path[i]], positions[path[i + 1]], 5)

# Graph Setup
G = nx.Graph()

# Define positions for the nodes (you can adjust these as necessary)
positions = {
    'Singapore': (SCREEN_WIDTH // 1.3, 450),
    'Vietnam': (SCREEN_WIDTH // 1.25, 350),
    'Turkey': (SCREEN_WIDTH // 3.1, 100),
    'China': (SCREEN_WIDTH // 1.17, 190),
    'India': (SCREEN_WIDTH // 1.65, 320),
    'Cape Town': (600, 400),  # Example, add actual coordinates
    'Suez Canal': (700, 200)  # Example, add actual coordinates
}

# Add nodes and edges (for now, random weights; you can replace with actual data)
for node in positions:
    G.add_node(node, pos=positions[node])

# Add weighted edges from adjacency matrix or custom data
G.add_edge('Singapore', 'Vietnam', weight=17)
G.add_edge('Singapore', 'China', weight=43)
G.add_edge('Vietnam', 'China', weight=28)
G.add_edge('Turkey', 'China', weight=100)
G.add_edge('India', 'Singapore', weight=39)
G.add_edge('Cape Town', 'Turkey', weight=83)
G.add_edge('Suez Canal', 'Turkey', weight=44)
G.add_edge('India', 'Suez Canal', weight=82)

# Button Class and Display Functions (unchanged)
class Button:
    def __init__(self, text, x, y, width, height, color, hover_color, shape, port_info=None, action=None):
        self.text = text
        self.rect = pygame.Rect(x, y, width, height)
        self.color = color
        self.hover_color = hover_color
        self.port_info = port_info
        self.action = action
        self.center = (x + width // 2, y + height // 2)
        self.radius = width // 2 if width == height else min(width, height) // 2
        self.shape = shape

    def draw(self, screen, font):
        mouse_pos = pygame.mouse.get_pos()
        is_hovered = self.rect.collidepoint(mouse_pos)
        if self.shape == "circle":
            pygame.draw.circle(screen, self.hover_color if is_hovered else self.color, self.center, self.radius)
        else:  # Draw rectangle
            pygame.draw.rect(screen, self.hover_color if is_hovered else self.color, self.rect)

        adjusted_font = font
        text_surf = font.render(self.text, True, BLACK)
        text_rect = text_surf.get_rect(center=self.center)
        screen.blit(text_surf, text_rect)
        return is_hovered

    def check_click(self, event):
        if event.type == pygame.MOUSEBUTTONDOWN:
            if self.rect.collidepoint(event.pos):
                if self.action:
                    self.action()
                    return True
                
def start_game():
    global current_page
    current_page = "game"

def data_game():
    global current_page
    current_page = "data"

def next_game():
    global current_page
    current_page = "next"

def draw_text_with_solid_border(text, font, text_color, border_color, x, y, padding=10):
    text_surf = font.render(text, True, text_color)
    text_rect = text_surf.get_rect(center=(x, y))
    border_rect = text_rect.inflate(padding, padding)
    pygame.draw.rect(screen, border_color, border_rect)
    screen.blit(text_surf, text_rect)
route_1 = [(SCREEN_WIDTH // 2.8, 140),(400, 120),(300, 100), (100, 130), (50, 300),(70, 400), (340, 850), (600, 830),(1030,400),(SCREEN_WIDTH // 1.54,350),(SCREEN_WIDTH // 1.24 , 480)]
route_2 = [(SCREEN_WIDTH // 2.8, 140),(560,200), (600, 250), (670, 360),(1030,400),(SCREEN_WIDTH // 1.54,350),(SCREEN_WIDTH // 1.24 , 480)]
route_3=[(SCREEN_WIDTH // 2.8, 100),(600,90),(740,70),(800,40),(1000,40),(SCREEN_WIDTH // 1.1, 210),(SCREEN_WIDTH // 1.18, 350),(1520,120)]

# Define colors for the routes
route_colors = [(255, 0, 0), (0, 0, 255),(0, 255, 0)]  # Red and Blue for different routes

start_button = Button("Start", SCREEN_WIDTH // 2 - 100, 500, 200, 80, GRAY, BLUE,"rect","", start_game)
#Singapore_button = Button("Singapore", SCREEN_WIDTH // 1.3 , 450, 120, 40, GRAY, BLUE,"circle", data_game)
#India_button = Button("India", SCREEN_WIDTH // 1.65 , 320, 120, 40, GRAY, BLUE,"circle", data_game)
#Turkey_button = Button("Turkey", SCREEN_WIDTH // 3.1 , 100, 120, 40, GRAY, BLUE,"circle", data_game)
#China_button = Button( "China",SCREEN_WIDTH // 1.17, 190, 120, 40, GRAY, BLUE, "circle",data_game)
#Vietnam_button = Button("Vietnam", SCREEN_WIDTH // 1.25, 350, 120, 40, GRAY, BLUE, "circle",data_game)
back_button = Button("Back", SCREEN_WIDTH // 2000, 0, 120, 40, GRAY, RED,"rect","", start_game)
Next_button = Button("Next", SCREEN_WIDTH // 1.08, 0, 120, 40, GRAY, GREEN,"rect","", data_game)
Previous_button = Button("Previous", SCREEN_WIDTH // 1900, 0, 150, 40, GRAY, GREEN,"rect","", data_game)
ports_data['Country'] = ports_data['Country'].str.strip()
new_ports_data['Country'] = new_ports_data['Country'].str.strip()
#Singapore_data = ports_data[ports_data['Country'] == 'Singapore']
#India_data = ports_data[ports_data['Country'] == 'India']
#Turkey_data = ports_data[ports_data['Country'] == 'Turkey']
#China_data = ports_data[ports_data['Country'] == 'China']
#Vietnam_data = ports_data[ports_data['Country'] == 'Vietnam']
#print(ports_data[ports_data['Country'] == 'Turkey'])
port_buttons = [
    Button("Singapore", SCREEN_WIDTH // 1.3, 450, 120, 40, GRAY, BLUE, "circle", new_ports_data[new_ports_data['Country'] == 'Singapore'], data_game),
    Button("India", SCREEN_WIDTH // 1.65, 320, 120, 40, GRAY, BLUE, "circle", new_ports_data[new_ports_data['Country'] == 'India'], data_game),
    Button("Turkey", SCREEN_WIDTH // 3.1, 100, 120, 40, GRAY, BLUE, "circle", new_ports_data[new_ports_data['Country'] == 'Turkey'], data_game),
    Button("China", SCREEN_WIDTH // 1.17, 190, 120, 40, GRAY, BLUE, "circle", new_ports_data[new_ports_data['Country'] == 'China'], data_game),
    Button("Vietnam", SCREEN_WIDTH // 1.25, 350, 120, 40, GRAY, BLUE, "circle",new_ports_data[new_ports_data['Country'] == 'Vietnam'], data_game)
]
def display_hover_info(port_info, x, y):
    lines = [
        f"Port: {port_info['Port'].values},",
        f"Country: {port_info['Country'].values},",
        f"Congestion: {port_info['Congestion'].values}%"
    ]
    text_height = len(lines) * 20
    border_rect = pygame.Rect(x - 300, y - 10, 500, text_height + 20)
    pygame.draw.rect(screen, (0, 0, 0), border_rect)
    pygame.draw.rect(screen, (200, 200, 200), border_rect.inflate(-5, -5))
    for i, line in enumerate(lines):
        text_surface = small_font.render(line, True, (0, 0, 0))
        screen.blit(text_surface, (x - 300, y + i * 20))


# Game Page (node selection + hover functionality)
def game_page():
    running = True
    start_node, end_node = None, None  # Track selected nodes

    while running:
        screen.blit(simulated_map, (0, 0))

        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                running = False

            # Node Selection Logic
            if event.type == pygame.MOUSEBUTTONDOWN:
                mouse_pos = event.pos
                for node, pos in positions.items():
                    if (pos[0] - mouse_pos[0])**2 + (pos[1] - mouse_pos[1])**2 < 400:
                        if not start_node:
                            start_node = node
                            print(f"Start node selected: {node}")
                        elif not end_node:
                            end_node = node
                            print(f"End node selected: {node}")

        # Draw routes or graph
        for node in G.nodes:
            pygame.draw.circle(screen, BLUE, positions[node], 20)
            text_surf = button_font.render(node, True, WHITE)
            screen.blit(text_surf, (positions[node][0] - 20, positions[node][1] - 10))

        for edge in G.edges(data=True):
            pygame.draw.line(screen, BLACK, positions[edge[0]], positions[edge[1]], 2)

        # If both nodes are selected, run Dijkstra and draw the shortest path
        if start_node and end_node:
            distances, previous_nodes = dijkstra(G, start_node)
            draw_shortest_path(previous_nodes, start_node, end_node)

        pygame.display.flip()
        clock.tick(60)

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
            if back_button.check_click(event)and current_port_index==0:
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
            """
            lines = [
                f"Port: {row['PortName']}",
                f"Country: {row['Country']}",
                f"Congestion: {row['Port Congestion(%)']}%",
                f"Container Berth: {row['Container Berth']}", 
                f"Area(ha): {row['Area(ha)']}",
                f"Designed Capacity(TEUs): {row['Designed Capacity(TEUs)']}",
                f"Suez Canal Risk: {row['Suez Canal Risk']}",
                f"Strait of Malacca Risk: {row['Strait of Malacca Risk']}",
                f"Bab el-Mandeb Risk: {row['Bab el-Mandeb Risk']}",
                f"South China Sea Risk: {row['South China Sea Risk']}",
                f"Indian Ocean Monsoon Risk: {row['Indian Ocean Monsoon Risk']}"
            ]"""

            lines = [
                f"Port: {row['Port']}",
                f"Country: {row['Country']}",
                f"Congestion: {row['Congestion']}%",
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

def main_menu():
    global current_page
    running = True
    while running:
        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                running = False
            start_button.check_click(event)
        
        screen.blit(world_map, (0, 0))
        draw_text_with_solid_border("Main Menu", font, BLACK, GRAY, SCREEN_WIDTH // 2, 100)
        start_button.draw(screen,button_font)
        draw_text_with_solid_border("Ming Kai", small_font, BLACK, GRAY, SCREEN_WIDTH // 2, 630)
        draw_text_with_solid_border("Wei Hao", small_font, BLACK, GRAY, SCREEN_WIDTH // 2, 670)
        draw_text_with_solid_border("Chris", small_font, BLACK, GRAY, SCREEN_WIDTH // 2, 710)

        pygame.display.flip()
        clock.tick(60)
        
        if current_page == "game":
            game_page()

        
    
    pygame.quit()
    sys.exit()
    
if __name__ == "__main__":
    current_page = "menu"
    main_menu()
