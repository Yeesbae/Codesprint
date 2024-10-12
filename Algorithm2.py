import pandas as pd
import numpy as np
import math

# Load the adjacency matrix from 'port_network.csv'
adjacency_matrix_file = 'port_network.csv'
adj_matrix = pd.read_csv(adjacency_matrix_file, index_col=0)

# Load the port data from 'Aggregated_Ports_By_Country.csv'
ports_data_file = 'Aggregated_Ports_By_Country.csv'
df_ports = pd.read_csv(ports_data_file)

# Clean up column and index names (strip leading/trailing spaces)
df_ports['Country'] = df_ports['Country'].str.strip()
adj_matrix.columns = adj_matrix.columns.str.strip()
adj_matrix.index = adj_matrix.index.str.strip()

# Artificial Data to mimic weight calculation for Cape Town and Suez Canal
manual_data = pd.DataFrame({
    'Country': ['Cape Town', 'Suez Canal'],
    'Total_Berths': [10, 8],
    'Total_Area_ha': [100, 120],
    'Total_Designed_Capacity_TEUs': [2000000, 3000000],
    'Avg_Congestion_Percentage': [70, 80]
})

# Append manual data to df_ports
df_ports = pd.concat([df_ports, manual_data], ignore_index=True)

# Normalize the port data (min-max normalization)
normalized_df = df_ports.copy()
for column in ['Total_Berths', 'Total_Area_ha', 'Total_Designed_Capacity_TEUs', 'Avg_Congestion_Percentage']:
    normalized_df[column] = (df_ports[column] - df_ports[column].min()) / (df_ports[column].max() - df_ports[column].min())

# Define geographical coordinates for the ports
port_locations = {
    'Singapore': (1.290270, 103.851959),
    'Vietnam': (14.058324, 108.277199),
    'Turkey': (38.963745, 35.243322),
    'China': (35.861660, 104.195397),
    'India': (20.593684, 78.962880),
    'Cape Town': (-33.918861, 18.424055),
    'Suez Canal': (30.585164, 32.559899)
}

# Haversine formula to calculate distance between two lat/lon points
def haversine(coord1, coord2):
    # Radius of the Earth in kilometers
    R = 6371.0
    lat1, lon1 = coord1
    lat2, lon2 = coord2

    # Convert latitude and longitude from degrees to radians
    lat1_rad = math.radians(lat1)
    lon1_rad = math.radians(lon1)
    lat2_rad = math.radians(lat2)
    lon2_rad = math.radians(lon2)

    # Differences between the latitudes and longitudes
    dlat = lat2_rad - lat1_rad
    dlon = lon2_rad - lon1_rad

    # Haversine formula
    a = math.sin(dlat / 2)**2 + math.cos(lat1_rad) * math.cos(lat2_rad) * math.sin(dlon / 2)**2
    c = 2 * math.atan2(math.sqrt(a), math.sqrt(1 - a))

    distance = R * c  # Distance in kilometers
    return distance

# Function to calculate the weight between two ports
def calculate_weight(port1, port2, alpha=1, beta=1, gamma=1, delta=1):
    # Calculate geographical distance using the Haversine formula
    if port1 in port_locations and port2 in port_locations:
        distance = haversine(port_locations[port1], port_locations[port2])
    else:
        print(f"Location missing for {port1} or {port2}")
        return 0  # No connection or invalid ports

    # Handle specific cases (e.g., non-ideal Turkey-China route via rail)
    if (port1 == 'Turkey' and port2 == 'China') or (port1 == 'China' and port2 == 'Turkey'):
        print(f"Non-ideal rail route detected between {port1} and {port2}. Increasing weight.")
        distance *= 1.5  # Arbitrary multiplier to account for rail inefficiency

    # Fetch port data for congestion and capacity
    port1_data = normalized_df.loc[normalized_df['Country'] == port1]
    port2_data = normalized_df.loc[normalized_df['Country'] == port2]

    if port1_data.empty or port2_data.empty:
        print(f"Port data missing for: {port1} or {port2}")
        return 0

    # Calculate weight based on congestion and capacity
    congestion_weight = alpha * port1_data['Avg_Congestion_Percentage'].values[0] + beta * port2_data['Avg_Congestion_Percentage'].values[0]
    capacity_weight = gamma * (port1_data['Total_Designed_Capacity_TEUs'].values[0] + port2_data['Total_Designed_Capacity_TEUs'].values[0])

    # Final weight calculation (penalty for rail routes applied)
    weight = congestion_weight + distance - capacity_weight
    
    # Ensure the weight is positive
    return max(weight, 0)

# Create a new DataFrame for storing the weighted adjacency matrix
weighted_adj_matrix = adj_matrix.copy()

# Calculate the weights for each connection in the adjacency matrix
weights = []  # Store all non-zero weights for scaling
for port1 in adj_matrix.index:
    for port2 in adj_matrix.columns:
        if adj_matrix.loc[port1, port2] == 1:  # Only process valid connections
            weight = calculate_weight(port1, port2)
            weighted_adj_matrix.loc[port1, port2] = weight
            if weight > 0:
                weights.append(weight)
        else:
            weighted_adj_matrix.loc[port1, port2] = 0  # No connection

# Apply min-max scaling to the weights
min_weight = min(weights)
max_weight = max(weights)

# Scaling function to rescale weights between a new range (e.g., 1 to 100)
def scale_weight(weight, min_weight, max_weight, new_min=1, new_max=100):
    if weight == 0:
        return 0
    return ((weight - min_weight) / (max_weight - min_weight)) * (new_max - new_min) + new_min

# Apply scaling to the weighted matrix
for port1 in weighted_adj_matrix.index:
    for port2 in weighted_adj_matrix.columns:
        weighted_adj_matrix.loc[port1, port2] = scale_weight(weighted_adj_matrix.loc[port1, port2], min_weight, max_weight)

# Save the scaled weighted adjacency matrix to a CSV file
weighted_adj_matrix.to_csv('adjacency_matrix2.csv')

print("Scaled weighted adjacency matrix saved to 'adjacency_matrix2.csv'")
