import joblib
import numpy as np
from sklearn.preprocessing import LabelEncoder
import pandas as pd



model_file = 'logistic_regression_model.joblib'
model = joblib.load(model_file)

port_info_csv = 'aggregated_ports_by_country.csv'
port_info = pd.read_csv(port_info_csv)

adjacency_matrix_csv = 'port_adjacency_matrix_c.csv'
adjacency_matrix = pd.read_csv(adjacency_matrix_csv)

adjacency_matrix_copy = adjacency_matrix.copy()