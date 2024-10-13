#Importing Modules
import pygame
import sys
import pandas as pd

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
        f"Congestion: {new_port_info['Congestion'].values}%"
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
    
def draw_text_with_solid_border(text, font, text_color, border_color, x, y, padding=10):
    text_surf = font.render(text, True, text_color)
    text_rect = text_surf.get_rect(center=(x, y))
    border_rect = text_rect.inflate(padding, padding)
    pygame.draw.rect(screen, border_color, border_rect)
    screen.blit(text_surf, text_rect)

def set_weight(country):
    global matrix_values
    for i in range(len(matrix_values)):
        for j in range(len(matrix_values[i])):
            if(i == country or j == country) and (matrix_values[i][j] != 0):
                matrix_values[i][j] = 100
            
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

countrycoed = {
    "Singapore": [SCREEN_WIDTH // 1.3, 450],
    "India": [SCREEN_WIDTH // 1.65, 320],
    "Turkey": [SCREEN_WIDTH // 3.1, 100],
    "China": [SCREEN_WIDTH // 1.17, 190],
    "Vietnam": [SCREEN_WIDTH // 1.25, 350],
    "CapeTown": [SCREEN_WIDTH // 4.25, 800],
    "SuezCanal": [SCREEN_WIDTH // 3.13, 155]
}
countrycoed_routes = {
    "Singapore": [SCREEN_WIDTH // 1.3 + 60, 450],
    "India": [SCREEN_WIDTH // 1.65 + 60, 320],
    "Turkey": [SCREEN_WIDTH // 3.1 + 60, 100],
    "China": [SCREEN_WIDTH // 1.17 + 60, 190],
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
        
        Simulate_button.draw(screen,small_font)

        pygame.display.flip()
        clock.tick(60)
        
        if current_page == "simulate":
            simulate_page()

        
    
    pygame.quit()
    sys.exit()

def simulate_page():
    running = True
    global matrix_values
    print(matrix_values)

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
