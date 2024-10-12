import pandas as pd
import numpy as np

# Load the data from the provided Excel file
file_path = 'data_mk.xlsx'
df = pd.read_excel(file_path)

# Function to generate 30 random variations of the original data with +-20% of the original values
def generate_randomized_data(df, num_samples=30, variation=0.2):
    all_data = []

    # Define columns to apply the variation
    columns_to_modify = ['Berth', 'Quay length', 'Area', 'Max Depth', 'Quay Cranes', 'Capacity (‘000 TEUs)', 'Congestion']

    for _ in range(num_samples):
        new_sample = df.copy()
        for column in columns_to_modify:
            if column in df.columns:
                # Ensure the column is numeric
                if pd.api.types.is_numeric_dtype(df[column]):
                    # Apply a random variation factor between 1-20% for each numeric value
                    variation_factor = np.random.uniform(1 - variation, 1 + variation, size=df[column].shape)

                    # Ensure integer values for 'Berth' and 'Quay Cranes' columns
                    if column in ['Berth', 'Quay Cranes','Capacity (‘000 TEUs)']:
                        new_sample[column] = (df[column] * variation_factor).round().astype(int)
                    else:
                        new_sample[column] = df[column] * variation_factor
                else:
                    print(f"Skipping non-numeric column: {column}")
        
        # Append the new randomized sample to the list
        all_data.append(new_sample)

    # Combine all samples into a single DataFrame
    randomized_data = pd.concat(all_data, ignore_index=True)
    return randomized_data

# Generate 30 random samples with the +-20% variation
randomized_data = generate_randomized_data(df)

# Save the randomized data to a new Excel file
output_file = 'randomized_30_samples_mk.xlsx'
randomized_data.to_excel(output_file, index=False)

print(f"Randomized data saved to {output_file}")
