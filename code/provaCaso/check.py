import pandas as pd


df = pd.read_csv('provaCaso/testing_df.csv')

df['date'] = pd.to_datetime(df['date'])

# Arrotonda i timestamp al secondo più vicino
df['date'] = df['date'].dt.floor('S')

# Calcola la differenza tra timestamp consecutivi
df['diff'] = df['date'].diff().dt.total_seconds()

# Trova dove la differenza è maggiore di 1 secondo, ignorando il primo elemento che è NaT
missing_seconds = df[df['diff'] > 1]

# Visualizza i secondi mancanti, se presenti
print("Missing single seconds at indices:", missing_seconds.index.tolist())
