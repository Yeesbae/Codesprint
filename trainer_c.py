import numpy as np
from sklearn.model_selection import train_test_split
from sklearn.linear_model import LogisticRegression
from sklearn.metrics import accuracy_score
import pandas as pd

# Example port data: [Berth, Quay Length (m), Area (ha), Max Depth (m), Quay Cranes,Capacity (‘000 TEUs)]

file_path = 'randomized_30_samples.xlsx'
df = pd.read_excel(file_path)

new_df = df.drop(['Port', 'Country'], axis=1)
data = new_df.values.tolist()

new_df = new_df.replace({',': ''}, regex=True)
new_df = new_df.apply(pd.to_numeric, errors='coerce')

X = np.array(data)
    
# Target variable: 1 for high congestion, 0 for low congestion
y = np.where(
    (new_df['Capacity (‘000 TEUs)'] >= 300) & 
    (new_df['Berth'] >= 11) & 
    (new_df['Area (ha)'] >= 40) &
    (new_df['Quay Cranes'] >= 20) &
    (new_df['Quay Length (m)'] >= 1000), 
    1, 
    0
)
print(X)

X_train, X_test, y_train, y_test = train_test_split(X, y, test_size=0.4, random_state=42)

model = LogisticRegression(solver='lbfgs', max_iter=350)

model.fit(X_train, y_train)

y_pred = model.predict(X_test)

accuracy = accuracy_score(y_test, y_pred)
print(f"Accuracy: {accuracy:.2f}")

new_ports = np.array([
    [51,18780,810,23,198,41154,0.03]
])

predicted_congestion = model.predict(new_ports)

for i, prediction in enumerate(predicted_congestion):
    print(f"New Port {i+1} Predicted Congestion Level: {'High' if prediction == 1 else 'Low'}")

all_ports_predictions = model.predict(X)
for i, prediction in enumerate(all_ports_predictions):
    print(f"Port {i} Predicted Congestion Level: {'High' if prediction == 1 else 'Low'}")