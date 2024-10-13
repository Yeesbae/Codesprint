import pandas as pd

# Sample DataFrame from the given CSV data
data = {
    'PortName': ['PSA Singapore', 'PSA Genova Pra', 'PSA Venice', 'PSA Sech', 'Dalian Container Terminal', 
                 'Fuzhou Container Terminal', 'Guangzhou Container Terminal', 'Tianjin Terminal', 'Lyg-PSA Container Terminal', 
                 'Beibu-Gulf International Container Terminal', 'SP-PSA International Port', 'Tan Cang Que Vo Inland Container Depot', 
                 'PSA Mumbai', 'PSA Chennai', 'PSA Sicla', 'PSA Kolkata'],
    'Country': ['Singapore', 'Italy', 'Italy', 'Italy', 'China', 'China', 'China', 'China', 'China', 'China', 
                'Vietnam', 'Vietnam', 'India', 'India', 'India', 'India'],
    'Container Berth': [55, 4, 5, 2, 14, 10, 4, 10, 5, 6, 2, 3, 3, 3, 1, 5],
    'Area(ha)': [810, 116, 28.3, 19.5, 235, 261, 28, 281, 83, 151.8, 27, 9.6, 100, 28, 10, 13.3],
    'Designed Capacity(TEUs)': [43900000, 2000000, 430000, 550000, 6600000, 4680000, 1300000, 6100000, 2800000, 5200000, 
                                740000, 248000, 2400000, 1400000, 450000, 850000],
    'Port Congestion(%)': [85, 75, 60, 50, 70, 65, 80, 75, 60, 55, 70, 45, 75, 70, 40, 60]
}

df = pd.DataFrame(data)

# Grouping by 'Country' and calculating the total container berths, total area, total designed capacity, and average congestion
aggregated_df = df.groupby('Country').agg(
    Total_Berths=('Container Berth', 'sum'),
    Total_Area_ha=('Area(ha)', 'sum'),
    Total_Designed_Capacity_TEUs=('Designed Capacity(TEUs)', 'sum'),
    Avg_Congestion_Percentage=('Port Congestion(%)', 'mean')
).reset_index()

# Display the aggregated DataFrame
aggregated_df

# Save the aggregated data to a CSV file
aggregated_df.to_csv('Aggregated_Ports_By_Country.csv', index=False)

print("CSV file saved as 'Aggregated_Ports_By_Country.csv'")
