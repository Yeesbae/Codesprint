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
data = pd.read_csv('PSA_Ports_Data.csv')
ports_data = data[["PortName", "Country", "Latitude", "Longitude", "Port Congestion(%)"]]

#Color Constants
WHITE = (255, 255, 255)
BLACK = (0, 0, 0)
GRAY = (150, 150, 150)
BLUE = (0, 0, 255)
RED = (255, 0, 0)

#Fonts Constants
font = pygame.font.Font(None, 74)
button_font = pygame.font.Font(None, 50)
small_font = pygame.font.Font(None, 36)

#Loading the images
world_map = pygame.image.load('PSA-Global-Network-1.png')
world_map = pygame.transform.scale(world_map, (SCREEN_WIDTH, SCREEN_HEIGHT))
simulated_map = pygame.image.load("LocationMap.png")
simulated_map = pygame.transform.scale(simulated_map, (SCREEN_WIDTH, SCREEN_HEIGHT))

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
        if event.type == pygame.MOUSEBUTTONDOWN:
            if self.rect.collidepoint(event.pos):
                if self.action:
                    self.action()

def display_hover_info(port_info, x, y):
    """Display the port info at a specified position (x, y) with a rectangle border."""
    # Define the lines of text to display
    lines = [
        f"Port: {port_info['PortName']}",
        f"Country: {port_info['Country']}",
        f"Congestion: {port_info['Port Congestion(%)']}%"
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

def draw_text_with_solid_border(text, font, text_color, border_color, x, y, padding=10):
    text_surf = font.render(text, True, text_color)
    text_rect = text_surf.get_rect(center=(x, y))
    border_rect = text_rect.inflate(padding, padding)
    pygame.draw.rect(screen, border_color, border_rect)
    screen.blit(text_surf, text_rect)

# Define Routes (List of waypoints for each route)
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
back_button = Button("Back", SCREEN_WIDTH // 1.08, 0, 120, 40, GRAY, RED,"rect","", start_game)

port_buttons = [
    Button("Singapore", SCREEN_WIDTH // 1.3, 450, 120, 40, GRAY, BLUE, "circle", ports_data.iloc[0], data_game),
    Button("India", SCREEN_WIDTH // 1.65, 320, 120, 40, GRAY, BLUE, "circle", ports_data.iloc[1], data_game),
    Button("Turkey", SCREEN_WIDTH // 3.1, 100, 120, 40, GRAY, BLUE, "circle", ports_data.iloc[2], data_game),
    Button("China", SCREEN_WIDTH // 1.17, 190, 120, 40, GRAY, BLUE, "circle", ports_data.iloc[3], data_game),
    Button("Vietnam", SCREEN_WIDTH // 1.25, 350, 120, 40, GRAY, BLUE, "circle", ports_data.iloc[4], data_game)
]

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

        hovered_button = None  # Reset hovered button for the frame
        for button in port_buttons:
            # Draw each button and check for hover
            if button.draw(screen, button_font):
                hovered_button = button  # Save hovered button for displaying info

        # Draw routes
        for route, color in zip([route_1, route_2, route_3], route_colors):
            pygame.draw.lines(screen, color, False, route, 5)  # '5' is the line thickness

        # Display hover info if there's a hovered button with associated port_info
        if hovered_button and hovered_button.port_info is not None:  # Check if port_info is not None
            display_hover_info(hovered_button.port_info, pygame.mouse.get_pos()[0], pygame.mouse.get_pos()[1])

        pygame.display.flip()
        clock.tick(60)
        if current_page == "data":
            data_page()

    pygame.quit()
    sys.exit()
def data_page():
    running = True
    while running:
        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                running = False
            back_button.check_click(event)
        
        screen.blit(world_map, (0, 0))
        back_button.draw(screen,button_font)
        pygame.display.flip()
        clock.tick(60)
        if current_page=="game":
            game_page()

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
