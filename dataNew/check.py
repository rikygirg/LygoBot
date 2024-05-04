import pandas as pd

# Leggi il file CSV
df = pd.read_csv('dataNew/dataset_num_1.csv')

# Filtra le righe dove la colonna 'Cross' è 1.0
print(df[df['Cross'] == 1.0])
