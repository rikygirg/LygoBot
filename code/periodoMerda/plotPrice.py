import pandas as pd
import matplotlib.pyplot as plt

class DataGrapher:
    def __init__(self, data_folder, col="close"):
        self.data_folder = data_folder
        self.col = col  # 'close' is the default column name
        self.current_df = 1  # Assuming you start numbering from 1

    def plot_close_column(self, num_files, sampling_rate=1000):
        plt.figure(figsize=(15, 6))  # Larger figure size for better visibility

        # Offset to continue the index from the last dataset
        index_offset = 0
        
        # To keep track if any data was plotted
        data_plotted = False

        # Iterate through the dataset files
        for i in range(1, num_files + 1):
            file_path = f"{self.data_folder}/dataset_num_{i}.csv"
            try:
                # Load the data with pandas
                df = pd.read_csv(file_path)
                
                # Check if the close column exists
                if self.col not in df.columns:
                    print(f"Available columns in {file_path}: {df.columns.tolist()}")
                    continue
                
                # Sample the data for close column
                sampled_df = df[self.col][::sampling_rate]
                new_indices = sampled_df.index // sampling_rate + index_offset

                # Plotting the main data
                plt.plot(new_indices, sampled_df, label=f'Dataset {i}')

                # Plotting the Cross where it is 1.0, independently of the main data sampling
                if 'Cross' in df.columns:
                    cross_mask = df['Cross'] == 1.0
                    cross_points = df[cross_mask]
                    cross_indices = cross_points.index // sampling_rate + index_offset
                    plt.scatter(cross_indices, cross_points[self.col], color='red', marker='X', s=100, label='Cross' if i == 1 else "")

                # Update the index offset for the next dataset
                index_offset = new_indices[-1] + 1  # Start the next dataset at the next index
                data_plotted = True
            except Exception as e:
                print(f"Failed to process {file_path}: {str(e)}")
        
        if data_plotted:
            plt.title('Continuous Close Price Over Multiple Datasets')
            plt.xlabel('Sampled Index')
            plt.ylabel('Close Price')
            plt.legend()
            plt.show()
        else:
            print("No data was plotted due to errors or missing columns.")

# Usage
data_folder = 'periodoMerda'  # Replace with your actual data folder path
grapher = DataGrapher(data_folder)
grapher.plot_close_column(num_files=3, sampling_rate=1000)  # Adjust num_files and sampling_rate as needed
