import pandas as pd
import networkx as nx
import matplotlib.pyplot as plt

# Step 1: Load the weighted adjacency matrix from the CSV file and strip whitespace from node names
csv_file = 'adjacency_matrix.csv'  # Update with your actual file path
df = pd.read_csv(csv_file, index_col=0)
df.columns = df.columns.str.strip()  # Strip any whitespace from column names
df.index = df.index.str.strip()      # Strip any whitespace from index (node names)

# Step 2: Create an undirected graph from the weighted adjacency matrix
G = nx.Graph()

# Add nodes (the ports and chokepoints)
nodes = df.index.tolist()  # Get the list of nodes from the index
G.add_nodes_from(nodes)

# Add edges with weights (based on the adjacency matrix)
for i in range(len(df)):
    for j in range(i + 1, len(df)):  # Avoid double counting edges
        weight = df.iloc[i, j]
        if weight > 0:  # If there's a connection (non-zero weight)
            G.add_edge(df.index[i], df.columns[j], weight=weight)

# Step 3: Assign geographical positions (longitude and latitude approximations)
positions = {
    'Singapore': (103.851959, 1.290270),
    'Vietnam': (108.277199, 14.058324),
    'Turkey': (35.243322, 38.963745),
    'China': (104.195397, 35.861660),
    'India': (78.962880, 20.593684),
    'Cape Town': (18.424055, -33.918861),
    'Suez Canal': (32.559899, 30.585164)
}

# Step 4: Draw the graph with edge weights reflected in the edge widths
plt.figure(figsize=(10, 8))

# Define edge weights (thicker edges for higher weights)
edges = G.edges(data=True)
edge_weights = [G[u][v]['weight'] for u, v in G.edges()]

# Draw the graph with the edge weights visualized
nx.draw(G, pos=positions, with_labels=True, node_color="lightblue", node_size=1000,  # Reduced node size
        font_size=10, font_weight="bold", edge_color="gray", width=[weight / 10 for weight in edge_weights])

# Add labels to the edges to display the weights
edge_labels = {(u, v): f'{d["weight"]:.2f}' for u, v, d in edges}
nx.draw_networkx_edge_labels(G, pos=positions, edge_labels=edge_labels)

plt.title("Port Network Visualization with Weights from Adjacency Matrix")
plt.show()
