import pandas as pd
import searoute as sr  # Assuming this is the searoute module

# Load the adjacency matrix (port network)
adjacency_matrix_file = 'port_network.csv'  # Update with the path to your file
adj_matrix = pd.read_csv(adjacency_matrix_file, index_col=0)

# Load the port data with lat/long and Total Designed Capacity
ports_data_file = 'Aggregated_Ports_By_Country.csv'  # Update with the path to your file
df_ports = pd.read_csv(ports_data_file)

# Strip any extra spaces from the names
df_ports['Country'] = df_ports['Country'].str.strip()
adj_matrix.columns = adj_matrix.columns.str.strip()
adj_matrix.index = adj_matrix.index.str.strip()

# Map the lat/long and capacity to ports in a dictionary
port_locations = dict(zip(df_ports['Country'], zip(df_ports['Latitude'], df_ports['Longitude'])))
port_capacities = dict(zip(df_ports['Country'], df_ports['Total_Designed_Capacity_TEUs']))
port_fullness = dict(zip(df_ports['Country'], df_ports['Avg_Congestion_Percentage']))

# Initialize distance matrix
distance_matrix = adj_matrix.copy()

# Track all adjusted distances for normalization later
all_distances = []

for port1 in adj_matrix.index:
    for port2 in adj_matrix.columns:
        if port1 != port2 and adj_matrix.loc[port1, port2] == 1:
            if port1 in port_locations and port2 in port_locations:
                coord1 = port_locations[port1]
                coord2 = port_locations[port2]

                # Swap lat/lon for searoute API if it expects (longitude, latitude)
                coord1 = [coord1[1], coord1[0]]  # Change (latitude, longitude) to (longitude, latitude)
                coord2 = [coord2[1], coord2[0]]  # Change (latitude, longitude) to (longitude, latitude)

                # Use the searoute function
                try:
                    route = sr.searoute([coord1[0], coord1[1]], [coord2[0], coord2[1]])
                    distance = route.properties['length']  # Distance in nautical miles

                    # Incorporate Total Designed Capacity into the calculation
                    capacity1 = port_capacities[port1]
                    capacity2 = port_capacities[port2]
                    port_fullness1 = port_fullness[port1]
                    port_fullness2 = port_fullness[port2]

                    # Example: Adjust the distance by adding a fraction of the total capacity (you can adjust the formula)
                    combined_capacity = capacity1 * (1 - port_fullness1) + capacity2 * (1 - port_fullness2)
                    adjusted_distance = distance + combined_capacity * 0.001  # Adjust factor as needed

                    # Store the adjusted distance temporarily
                    all_distances.append(adjusted_distance)

                except Exception as e:
                    print(f"Error calculating route from {port1} to {port2}: {e}")
                    all_distances.append(0)  # Handle failure by setting 0 or another value

# Step 2: Normalize distances to ensure the values are scaled between 1 and 100
min_distance = min(all_distances) if all_distances else 0  # Ensure min is not zero for scaling
max_distance = max(all_distances) if all_distances else 1  # Avoid division by zero

# Initialize a counter to iterate through the normalized values
distance_index = 0

for port1 in adj_matrix.index:
    for port2 in adj_matrix.columns:
        if port1 != port2 and adj_matrix.loc[port1, port2] == 1:
            # Normalize the adjusted distance to be a value between 1 and 100, and convert to integer
            normalized_distance = int(((all_distances[distance_index] - min_distance) / (max_distance - min_distance)) * 99) + 1
            distance_matrix.loc[port1, port2] = normalized_distance
            distance_index += 1
        else:
            distance_matrix.loc[port1, port2] = 0  # No connection or invalid data

# Save the updated adjacency matrix with normalized distances
output_file = 'adjacency_matrix.csv'  # Specify your output file path
distance_matrix.to_csv(output_file)

print("Adjacency matrix with normalized distances saved to:", output_file)
