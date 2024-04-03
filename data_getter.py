import numpy as np
from tqdm import tqdm
from functions_file import save_data
import pandas as pd
import datetime as dt
import time
import os



def getData(timeframe, col, client, CURRENCY):
    symbol = CURRENCY
    interval = '1m'
    d = None
    while d is None:
        try:
            klines = client.get_historical_klines(symbol, interval, str(timeframe) + " min ago UTC")
            data = pd.DataFrame(klines)
            data.columns = ['open_time', 'open', 'high', 'low', 'close', 'volume', 'close_time', 'qav', 'num_trades',
                            'taker_base_vol', 'taker_quote_vol', 'ignore']
            data.index = [dt.datetime.fromtimestamp(x / 1000.0) for x in data.close_time]
            data['open_time'] = [dt.datetime.fromtimestamp(int(str(d)[:-3])) for d in data['open_time']]
            d = data[col].astype(float)
        except:
            pass
    return d

def get_period_data(lastData, db, client):
    tic = time.time()  # Record start time
    col = list(lastData.columns)
    lastTime = dt.datetime.strptime(db["lastTime"], '%H:%M:%S.%f')
    if (lastTime + dt.timedelta(minutes=1)).strftime("%H:%M") == dt.datetime.now().strftime("%H:%M"):
        db["lastTime"] = str(dt.datetime.now().strftime('%H:%M:%S.%f'))
        d = getData(2, col, client)
        lastData = lastData.drop([lastData.index[0], lastData.index[len(lastData) - 1]])
        lastData = pd.concat([lastData, d])
    else:
        lastData = lastData.drop([lastData.index[len(lastData) - 1]])
        d = getData(1, col, client)
        lastData = pd.concat([lastData, d])
    toc = time.time()  # Record end time
    elapsed_time = toc - tic  # Calculate elapsed time
    save_data("data_log_period.txt", str(len(lastData)) + "\n" + str(lastData))
    print(lastData)
    return elapsed_time, lastData


def get_current_price():
    # return client.get_symbol_ticker(symbol="BTCUSDT")["price"]
    return None


import pandas as pd

class Backtester:
    def __init__(self, data_folder, max_period, stop, columns=["close", "volume", "high", "low", "qav"], cdf = 0):
        self.tick = max_period * 60
        self.data_folder = data_folder
        self.columns = columns
        self.df1 = pd.DataFrame(columns=columns)
        self.df2 = pd.DataFrame(columns=columns)
        self.current_df = cdf
        file_path = f"{self.data_folder}/dataset_num_{self.current_df + 1}.csv"
        self.df1 = pd.read_csv(file_path)
        self.stop = stop
        self.pbar = tqdm(total=self.stop - self.tick)

    def getData(self, period, tick=None):
        #start_time = time.time()
        offset = self.tick % 60
        temp = self.tick - offset
        indices = [temp + i*60-1 for i in range(-period+2, 1)]
        indices.append(self.tick)
        data = self.df1.iloc[indices]
        data = data.drop(data.columns[0], axis=1)
        data = data.set_index('date')
        #end_time = time.time()
        #elapsed_time = end_time - start_time
        #print(elapsed_time)
        #print(data, len(data))
        self.tick += 1
        self.pbar.update(1)
        if self.tick == self.stop:
            self.pbar.close()
            return data, False
        else:
            return data, True
            



class Backtesting2:
    def __init__(self, file_path, chunk_size=32000, N_max=30):
        # Extract file name without extension
        file_name = os.path.splitext(os.path.basename(file_path))[0]

        # Create a folder name with the specified pattern
        folder_name = 'folderData_' + file_name

        # Create the folder path
        self.folder_path = os.path.join(os.path.dirname(file_path), folder_name)
        os.makedirs(self.folder_path, exist_ok=True)
        self.folder_path_row = os.path.join(os.path.dirname(os.path.join(self.folder_path, folder_name)), "row")
        os.makedirs(self.folder_path_row, exist_ok=True)
        self.folder_path_filtered = os.path.join(os.path.dirname(os.path.join(self.folder_path, folder_name)), "filtered")
        os.makedirs(self.folder_path_filtered, exist_ok=True)

        # Load the DataFrame from the specified CSV file with 'date' as index
        self.df = pd.read_csv(file_path)

        # Initialize tick to 0
        self.tick = 60 * 30

        # Set the maximum value of N
        self.N_max = N_max

        # Initialize the chunk-related attributes
        self.chunk_size = chunk_size
        self.num_chunks = len(self.df) // chunk_size

        self.chunk_file_paths_row = [os.path.join(self.folder_path_row, f'chunk_{i}.csv') for i in range(self.num_chunks)]
        self.chunk_file_paths_filtered = [os.path.join(self.folder_path_filtered, f'chunk_{i}.csv') for i in range(self.num_chunks)]

        # Call the before_filter method to split and load chunks
        self.before_filter()
        self.filter_and_save()

    def before_filter(self):
        # Check if the chunk files already exist
        if all(os.path.exists(chunk_file_path) for chunk_file_path in self.chunk_file_paths_row):
            print("Using existing chunk files.")
            return

        # Create a tqdm instance with the total number of iterations
        progress_bar = tqdm(total=self.num_chunks, desc="Splitting Database into Chunks")

        # Split the DataFrame into chunks and save each chunk as a separate file
        for i in range(self.num_chunks):
            chunk_start = i * self.chunk_size
            chunk_end = (i + 1) * self.chunk_size
            chunk_file_path = os.path.join(self.folder_path_row, f'chunk_{i}.csv')
            self.df.iloc[chunk_start:chunk_end].to_csv(chunk_file_path, index=False)

            # Update the progress bar
            progress_bar.update(1)

        # Close the progress bar
        progress_bar.close()

    def filter_and_save(self):

        # Check if the filtered folder already exists
        if all(os.path.exists(chunk_file_path) for chunk_file_path in self.chunk_file_paths_filtered):
            print("Using existing filtered files.")
            return

        # Create the filtered folder if it doesn't exist
        os.makedirs(self.folder_path_filtered, exist_ok=True)

        # Create a tqdm instance with the total number of iterations
        progress_bar = tqdm(total=self.num_chunks, desc="Filtering and Saving")

        for i in range(self.num_chunks):
            chunk_file_path = os.path.join(self.folder_path_row, f'chunk_{i}.csv')
            chunk_df = pd.read_csv(chunk_file_path)

            filtered_data = pd.DataFrame()
            j = 0
            start_index = 0
            while j < len(chunk_df):
                if chunk_df["date"].iloc[j][17:19] == "59":
                    start_index = j
                    break
                else:
                    j += 1
            j = len(chunk_df) - 1
            end_index = len(chunk_df)
            while j > 0:
                if chunk_df["date"].iloc[j][17:19] == "59":
                    end_index = j
                    break
                else:
                    j -= 1
            array = np.arange(0, 32000, 1)
            print(start_index, end_index)
            print(array[start_index:end_index+1:60])
            filtered_data = chunk_df.iloc[start_index:end_index+1:60]
            chunk_file_path_filtered = os.path.join(self.folder_path_filtered, f'chunk_{i}.csv')
            filtered_data.to_csv(chunk_file_path_filtered, index=False)
            # Update the progress bar
            progress_bar.update(1)

        # Close the progress bar
        progress_bar.close()

        print(f"Filtered data chunks saved to: {self.folder_path_filtered}")

    def get_data(self, N, col):
        # Check if there is enough data
        if self.tick >= len(self.df):
            print("Insufficient data for the given N.")
            return None

        # Load the filtered DataFrame
        filtered_file_path = os.path.join(self.folder_path, 'filtered_data.csv')
        filtered_df = pd.read_csv(filtered_file_path)

        output_df = pd.DataFrame(columns=col)
        n = 1

        while n <= N and self.tick < self.N_max:
            output_df = pd.concat([output_df, filtered_df.iloc[self.tick:self.tick + 1]])
            n += 1
            self.tick += 1

        return output_df


#file_path = "data/data1oct_14dec2023.csv"
#backtest_instance2 = Backtesting2(file_path)
#result_df2 = backtest_instance2.get_data(N=10, col=["close", "low"])
