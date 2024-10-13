import searoute as sr
import folium
import csv
import networkx as nx
import math
import heapq
import joblib as jb
import pandas as pd
import random
import matplotlib.pyplot as plt

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

def dijkstra(graph, start):
    distances = {node: float('infinity') for node in graph.nodes}
    distances[start] = 0
    priority_queue = [(0, start)]
    shortest_path_tree = {}

    while priority_queue:
        current_distance, current_node = heapq.heappop(priority_queue)

        if current_distance > distances[current_node]:
            continue

        for neighbor, attributes in graph[current_node].items():
            weight = attributes['weight']
            distance = current_distance + weight

            if distance < distances[neighbor]:
                distances[neighbor] = distance
                heapq.heappush(priority_queue, (distance, neighbor))
                shortest_path_tree[neighbor] = current_node

    return distances, shortest_path_tree

# def a_star(graph, start, goal):
#     open_set = set([start])
#     closed_set = set()
#     g_scores = {node: float('infinity') for node in graph.nodes}
#     g_scores[start] = 0
#     f_scores = {node: float('infinity') for node in graph.nodes}
#     f_scores[start] = haversine(graph.nodes[start]['pos'], graph.nodes[goal]['pos'])
#     came_from = {}

#     while open_set:
#         current = min(open_set, key=lambda node: f_scores[node])

#         if current == goal:
#             path = []
#             while current in came_from:
#                 path.append(current)
#                 current = came_from[current]
#             path.append(start)
#             path.reverse()
#             return path

#         open_set.remove(current)
#         closed_set.add(current)

#         for neighbor, attributes in graph[current].items():
#             if neighbor in closed_set:
#                 continue

#             tentative_g_score = g_scores[current] + attributes['weight']

#             if neighbor not in open_set:
#                 open_set.add(neighbor)
#             elif tentative_g_score >= g_scores[neighbor]:
#                 continue

#             came_from[neighbor] = current
#             g_scores[neighbor] = tentative_g_score
#             f_scores[neighbor] = g_scores[neighbor] + haversine(graph.nodes[neighbor]['pos'], graph.nodes[goal]['pos'])

#     return None

def normalize_distances(adjacency_matrix):
    all_distances = [distance for distances in adjacency_matrix.values() for distance in distances.values()]
    min_distance = min(all_distances)
    max_distance = max(all_distances)

    normalized_matrix = {}
    for start_port, distances in adjacency_matrix.items():
        normalized_matrix[start_port] = {
            port: 100 * (distance - min_distance) / (max_distance - min_distance) for port, distance in distances.items()
        }
    return normalized_matrix

def create_adjacency_matrix(graph, start_ports):
    adjacency_matrix = {}
    for start_port in start_ports:
        distances, _ = dijkstra(graph, start_port)
        adjacency_matrix[start_port] = distances
    return adjacency_matrix

def print_adjacency_matrix(matrix):
    ports = list(matrix.keys())
    header = "From/To".ljust(15) + "".join([port.ljust(15) for port in ports])
    print(header)
    for start_port in ports:
        row = start_port.ljust(15)
        for end_port in ports:
            row += f"{matrix[start_port][end_port]:.2f}".ljust(15)
        print(row)

def find_shortest_path(graph, start_node, target_node, min_weight, max_weight):
    def normalized_weight(u, v, d):
        return 100 * (d['weight'] - min_weight) / (max_weight - min_weight)

    try:
        path = nx.shortest_path(graph, source=start_node, target=target_node, weight=normalized_weight)
        distance = nx.shortest_path_length(graph, source=start_node, target=target_node, weight=normalized_weight)
        print(f"Shortest path from {start_node} to {target_node}: {path}")
        print(f"Total distance: {distance}")
        return path, distance
    except nx.NetworkXNoPath:
        print(f"No path found between {start_node} and {target_node}")
        return None, float('inf')

port_locations = {
    'Singapore': (1.290270, 103.851959),
    'Vietnam': (14.058324, 108.277199),
    'Turkey': (38.963745, 35.243322),
    'China': (35.861660, 104.195397),
    'India': (20.593684, 78.962880),
    'CapeTown': (-33.918861, 18.424055),
    'SuezCanal': (30.585164, 32.559899)
}

G = nx.Graph()

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

fig, axes = plt.subplots(nrows=3, ncols=3, figsize=(20, 15))
axes = axes.flatten()

for idx, start_port in enumerate(port_locations.keys()):
    distances, shortest_path_tree = dijkstra(G, start_port)
    
    ax = axes[idx]
    pos = nx.get_node_attributes(G, 'pos')
    nx.draw(G, pos, with_labels=True, node_color='skyblue', node_size=1000, font_size=10, font_weight='bold', ax=ax)
    
    tree_edges = [(node, shortest_path_tree[node]) for node in shortest_path_tree]
    nx.draw_networkx_edges(G, pos, edgelist=tree_edges, edge_color='green', width=2, ax=ax)
    
    tree_edge_labels = {(u, v): f"{G[u][v]['weight']:.2f}" for u, v in tree_edges}
    nx.draw_networkx_edge_labels(G, pos, edge_labels=tree_edge_labels, font_size=8, ax=ax)
    
    all_edge_labels = {(u, v): f"{d['weight']:.2f}" for u, v, d in G.edges(data=True)}
    nx.draw_networkx_edge_labels(G, pos, edge_labels=all_edge_labels, font_size=8, font_color='blue', ax=ax)
    
    ax.set_title(f"Shortest Path Tree from {start_port}")
    ax.text(0.5, 0.95, f"Starting Port: {start_port}", horizontalalignment='center', verticalalignment='center', transform=ax.transAxes, fontsize=12, bbox=dict(facecolor='white', alpha=0.6))

for idx in range(len(port_locations), len(axes)):
    fig.delaxes(axes[idx])

plt.tight_layout()
plt.show()

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
        

# print(country_ports)

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

fig, axes = plt.subplots(nrows=3, ncols=3, figsize=(20, 15))
axes = axes.flatten()

for idx, start_port in enumerate(port_locations.keys()):
    distances, shortest_path_tree = dijkstra(G, start_port)
    
    ax = axes[idx]
    pos = nx.get_node_attributes(G, 'pos')
    nx.draw(G, pos, with_labels=True, node_color='skyblue', node_size=1000, font_size=10, font_weight='bold', ax=ax)
    
    tree_edges = [(node, shortest_path_tree[node]) for node in shortest_path_tree]
    nx.draw_networkx_edges(G, pos, edgelist=tree_edges, edge_color='green', width=2, ax=ax)
    
    tree_edge_labels = {(u, v): f"{G[u][v]['weight']:.2f}" for u, v in tree_edges}
    nx.draw_networkx_edge_labels(G, pos, edge_labels=tree_edge_labels, font_size=8, ax=ax)
    
    all_edge_labels = {(u, v): f"{d['weight']:.2f}" for u, v, d in G.edges(data=True)}
    nx.draw_networkx_edge_labels(G, pos, edge_labels=all_edge_labels, font_size=8, font_color='blue', ax=ax)
    
    ax.set_title(f"Shortest Path Tree from {start_port}")
    ax.text(0.5, 0.95, f"Starting Port: {start_port}", horizontalalignment='center', verticalalignment='center', transform=ax.transAxes, fontsize=12, bbox=dict(facecolor='white', alpha=0.6))

for idx in range(len(port_locations), len(axes)):
    fig.delaxes(axes[idx])

plt.tight_layout()
plt.show()