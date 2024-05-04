import os
import pandas as pd

# Function to ensure the number of lines is divisible by 60
def ensure_divisible(df):
    num_rows = len(df)
    remainder = num_rows % 60
    if remainder != 0:
        df = df.iloc[:-remainder]
    return df

# Function to leave the first n lines of DataFrame
def leave_first_n(df, n):
    return df.iloc[:n]

# Path to the folder containing the CSV files
folder_path = 'provaCaso'

# Number of lines to leave
lines_to_leave = 10000

# Iterate over all CSV files in the folder
for file_name in os.listdir(folder_path):
    if file_name.endswith('.csv'):
        file_path = os.path.join(folder_path, file_name)
        
        # Read CSV file into a DataFrame
        df = pd.read_csv(file_path)
        
        # Ensure the number of lines is divisible by 60
        df = ensure_divisible(df)
        
        # Leave the first n lines of DataFrame
        trimmed_df = leave_first_n(df, lines_to_leave)
        
        # Save trimmed DataFrame to the same CSV file (override)
        trimmed_df.to_csv(file_path, index=False)

        print(f"Trimmed DataFrame saved to {file_path}")
