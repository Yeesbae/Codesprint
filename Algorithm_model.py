import joblib
import numpy as np
from sklearn.preprocessing import LabelEncoder
import pandas as pd


file_path = 'logistic_regression_model.joblib'
csv_file_path = 'data_mk.csv'

model = joblib.load(file_path)
data = pd.read_csv(csv_file_path)

filtered_data = data.drop(columns=['Port', 'Country'])
datasets = [row.values.reshape(1, -1) for index, row in filtered_data.iterrows()]

predictions = [model.predict(dataset) for dataset in datasets]
predictions = [prediction[0] for prediction in predictions]
predictions = pd.DataFrame(predictions, columns=['Predictions'])

print(predictions)