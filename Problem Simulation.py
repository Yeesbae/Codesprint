#Importing Modules
import pygame
import sys

pygame.init()

#Setting up the screen
SCREEN_WIDTH = 1600
SCREEN_HEIGHT = 900
screen = pygame.display.set_mode((SCREEN_WIDTH, SCREEN_HEIGHT))
pygame.display.set_caption("Algorithm Simulation")

clock = pygame.time.Clock()

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
    def __init__(self, text, x, y, width, height, color, hover_color, shape,action=None):
        self.text = text
        self.rect = pygame.Rect(x, y, width, height)
        self.color = color
        self.hover_color = hover_color
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

    def check_click(self, event):
        if event.type == pygame.MOUSEBUTTONDOWN:
            if self.rect.collidepoint(event.pos):
                if self.action:
                    self.action()

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

start_button = Button("Start", SCREEN_WIDTH // 2 - 100, 500, 200, 80, GRAY, BLUE,"rect", start_game)
Singapore_button = Button("Singapore", SCREEN_WIDTH // 1.3 , 450, 120, 40, GRAY, BLUE,"circle", data_game)
India_button = Button("India", SCREEN_WIDTH // 1.65 , 300, 120, 40, GRAY, BLUE,"circle", data_game)
Turkey_button = Button("Turkey", SCREEN_WIDTH // 3.1 , 100, 120, 40, GRAY, BLUE,"circle", data_game)
China_button = Button( "China",SCREEN_WIDTH // 1.17, 190, 120, 40, GRAY, BLUE, "circle",data_game)
Vietnam_button = Button("Vietnam", SCREEN_WIDTH // 1.25, 350, 120, 40, GRAY, BLUE, "circle",data_game)
back_button = Button("Back", SCREEN_WIDTH // 1.08, 0, 120, 40, GRAY, RED,"rect", start_game)

def game_page():
    running = True
    while running:
        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                running = False
            Singapore_button.check_click(event)
            India_button.check_click(event)
            Turkey_button.check_click(event)
            China_button.check_click(event)
            Vietnam_button.check_click(event)
        
        screen.blit(simulated_map, (0, 0))
        Singapore_button.draw(screen,button_font)
        India_button.draw(screen,button_font)
        Turkey_button.draw(screen,button_font)
        China_button.draw(screen,button_font)
        Vietnam_button.draw(screen,button_font)
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
