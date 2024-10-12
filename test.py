import pygame
import pandas as pd
import networkx as nx
import heapq

# Initialize Pygame
pygame.init()

# Constants
SCREEN_WIDTH, SCREEN_HEIGHT = 800, 600
WHITE = (255, 255, 255)
BLACK = (0, 0, 0)
RED = (255, 0, 0)
GREEN = (0, 255, 0)
BLUE = (0, 0, 255)
LIGHT_GRAY = (200, 200, 200)

# Font settings
font = pygame.font.SysFont(None, 24)

# Load adjacency matrix from CSV
adj_matrix_file = 'adjacency_matrix.csv'
df = pd.read_csv(adj_matrix_file, index_col=0)

# Initialize Pygame display
screen = pygame.display.set_mode((SCREEN_WIDTH, SCREEN_HEIGHT))
pygame.display.set_caption("Dijkstra's Algorithm Visualization")

# Graph object from NetworkX
G = nx.Graph()

# Define positions for the nodes (you can adjust these as necessary)
positions = {
    'Singapore': (100, 200),
    'Vietnam': (200, 100),
    'Turkey': (400, 200),
    'China': (500, 100),
    'India': (300, 300),
    'Cape Town': (600, 400),
    'Suez Canal': (700, 200)
}

# Add nodes
for node in df.index:
    G.add_node(node, pos=positions[node])

# Add weighted edges from the adjacency matrix
for i in df.index:
    for j in df.columns:
        if df.loc[i, j] > 0:  # Only add edges with a weight greater than 0
            G.add_edge(i, j, weight=df.loc[i, j])

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

# Function to draw the graph
def draw_graph():
    screen.fill(WHITE)
    for edge in G.edges(data=True):
        pygame.draw.line(screen, BLACK, positions[edge[0]], positions[edge[1]], 2)
        mid_x = (positions[edge[0]][0] + positions[edge[1]][0]) // 2
        mid_y = (positions[edge[0]][1] + positions[edge[1]][1]) // 2
        weight = edge[2]['weight']
        text = font.render(str(round(weight, 2)), True, BLACK)
        screen.blit(text, (mid_x, mid_y))
    
    for node, pos in positions.items():
        pygame.draw.circle(screen, BLUE, pos, 20)
        text = font.render(node, True, WHITE)
        screen.blit(text, (pos[0] - 20, pos[1] - 10))

# Draw the shortest path
def draw_shortest_path(previous_nodes, start_node, end_node):
    path = []
    while end_node:
        path.append(end_node)
        end_node = previous_nodes[end_node]
    path.reverse()

    # Draw the path in red
    for i in range(len(path) - 1):
        pygame.draw.line(screen, RED, positions[path[i]], positions[path[i + 1]], 5)

# Button class to modify weights
class Button:
    def __init__(self, text, x, y, w, h, action=None):
        self.text = text
        self.rect = pygame.Rect(x, y, w, h)
        self.action = action

    def draw(self, screen):
        pygame.draw.rect(screen, LIGHT_GRAY, self.rect)
        text_surface = font.render(self.text, True, BLACK)
        text_rect = text_surface.get_rect(center=self.rect.center)
        screen.blit(text_surface, text_rect)

    def check_click(self, event):
        if event.type == pygame.MOUSEBUTTONDOWN and self.rect.collidepoint(event.pos):
            if self.action:
                self.action()

# Modify weight function
def modify_weight(node1, node2, new_weight):
    G[node1][node2]['weight'] = new_weight
    G[node2][node1]['weight'] = new_weight
    df.loc[node1, node2] = new_weight
    df.loc[node2, node1] = new_weight

# Main game loop
def main():
    running = True
    start_node, end_node = None, None
    buttons = [
        Button("Change Weight (Singapore-Vietnam)", 50, 500, 250, 40, lambda: modify_weight('Singapore', 'Vietnam', 10)),
        Button("Change Weight (Singapore-China)", 350, 500, 250, 40, lambda: modify_weight('Singapore', 'China', 50)),
    ]

    while running:
        draw_graph()

        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                running = False

            # Click event to select start and end nodes
            if event.type == pygame.MOUSEBUTTONDOWN:
                mouse_pos = event.pos
                for node, pos in positions.items():
                    if (pos[0] - mouse_pos[0])**2 + (pos[1] - mouse_pos[1])**2 < 400:  # 20^2 = 400 for circle radius
                        if not start_node:
                            start_node = node
                            print(f"Start node selected: {node}")
                        elif not end_node:
                            end_node = node
                            print(f"End node selected: {node}")
            
            # Check button clicks
            for button in buttons:
                button.check_click(event)

        # Draw buttons
        for button in buttons:
            button.draw(screen)

        # Run Dijkstra's if both start and end nodes are selected
        if start_node and end_node:
            distances, previous_nodes = dijkstra(G, start_node)
            draw_shortest_path(previous_nodes, start_node, end_node)

        pygame.display.flip()

    pygame.quit()

if __name__ == "__main__":
    main()
