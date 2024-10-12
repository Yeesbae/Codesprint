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
    def __init__(self, text, x, y, width, height, color, hover_color, action=None):
        self.text = text
        self.rect = pygame.Rect(x, y, width, height)
        self.color = color
        self.hover_color = hover_color
        self.action = action

    def draw(self, screen):
        mouse_pos = pygame.mouse.get_pos()
        if self.rect.collidepoint(mouse_pos):
            pygame.draw.rect(screen, self.hover_color, self.rect)
        else:
            pygame.draw.rect(screen, self.color, self.rect)
        
        text_surf = button_font.render(self.text, True, BLACK)
        text_rect = text_surf.get_rect(center=self.rect.center)
        screen.blit(text_surf, text_rect)

    def check_click(self, event):
        if event.type == pygame.MOUSEBUTTONDOWN:
            if self.rect.collidepoint(event.pos):
                if self.action:
                    self.action()

def start_game():
    global current_page
    current_page = "game"

def draw_text_with_solid_border(text, font, text_color, border_color, x, y, padding=10):
    text_surf = font.render(text, True, text_color)
    text_rect = text_surf.get_rect(center=(x, y))
    border_rect = text_rect.inflate(padding, padding)
    pygame.draw.rect(screen, border_color, border_rect)
    screen.blit(text_surf, text_rect)

start_button = Button("Start", SCREEN_WIDTH // 2 - 100, 500, 200, 80, GRAY, BLUE, start_game)

def game_page():
    running = True
    while running:
        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                running = False
        
        screen.blit(simulated_map, (0, 0))
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
        
        screen.blit(world_map, (0, 0))
        draw_text_with_solid_border("Main Menu", font, BLACK, GRAY, SCREEN_WIDTH // 2, 100)
        start_button.draw(screen)
        draw_text_with_solid_border("User 1", small_font, BLACK, GRAY, SCREEN_WIDTH // 2, 630)
        draw_text_with_solid_border("User 2", small_font, BLACK, GRAY, SCREEN_WIDTH // 2, 670)
        draw_text_with_solid_border("User 3", small_font, BLACK, GRAY, SCREEN_WIDTH // 2, 710)

        pygame.display.flip()
        clock.tick(60)
        
        if current_page == "game":
            game_page()
    
    pygame.quit()
    sys.exit()

if __name__ == "__main__":
    current_page = "menu"
    main_menu()
