import sys
import pandas as pd
import datetime as dt
from binance import Client
import numpy as np
from tqdm import tqdm

api_key = '##########'
api_secret = '##########'
client = Client(api_key, api_secret)


def get_historical_data(symbol, categories=['close'], interval='1m', start_string="60m min ago UTC", end_string=None):
    """
    Retrieve historical data for a given symbol, interval, and categories.

    Parameters:
    - symbol: The trading pair symbol (e.g., "BTCUSDT").
    - categories: A list of categories to retrieve (e.g., ['close', 'low', 'high']).
    - interval: The interval for the historical data (default: '1m').
    - start_string: The starting time in string format (default: "60m min ago UTC").
    - end_string: The ending time in string format (default: None).

    Returns:
    - A DataFrame containing the specified categories.
    """
    klines = None
    while klines is None:
        try:
            klines = client.get_historical_klines(symbol, interval, start_str=start_string, end_str=end_string)
            break
        except Exception as e:
            print(f"Error fetching data: {e}")

    data = pd.DataFrame(klines, columns=['open_time', 'open', 'high', 'low', 'close', 'volume', 'close_time',
                                         'qav', 'num_trades', 'taker_base_vol', 'taker_quote_vol', 'ignore'])
    data['close_time'] = pd.to_datetime(data['close_time'], unit='ms')

    return data[categories], data['close_time'].to_numpy()


def minute_compressor(df):
    """
    Compress DataFrame by grouping data by minute and taking the last entry in each group.

    Parameters:
    - df: The DataFrame to be compressed.

    Returns:
    - The compressed DataFrame.
    """
    return df.groupby(np.arange(len(df)) // 60).tail(1)

def datetime_to_unix_timestamp(date):
    return int(((date - dt.datetime(1970, 1, 1)).total_seconds() - 3600) * 1000)

def get_formatted_data(start_date, end_date=None, interval='1s', categories=None, folder_path="data"):
    if categories is None:
        categories = ['close']
    start_time = datetime_to_unix_timestamp(pd.to_datetime(start_date, format='%d %B %Y %H:%M:%S.%f'))
    end_time = datetime_to_unix_timestamp(pd.to_datetime(end_date, format='%d %B %Y %H:%M:%S.%f'))
    if not end_date:
        end_time = datetime_to_unix_timestamp(dt.datetime.now()) // 1000 * 1000
    total_seconds = (end_time - start_time)/1000

    dates = []
    i = start_time
    batch_size = 960
    while i < end_time:
        dates.append(i)
        i += 1000 * batch_size
    chunks = []
    for k in range(len(dates)):
        if k % 1000 == 0 and k != 0:
            chunks.append(k)
    d = 0
    with tqdm(total=total_seconds, unit='sec', desc='Progress', file=sys.stdout) as pbar:
        dfs = []
        while d < len(dates)-1:
            start_str = f"{dates[d]}"
            end_str = f"{dates[d+1]-1000}"
            block, datas = get_historical_data("BTCUSDT", categories=categories, interval="1s",
                                               start_string=start_str, end_string=end_str)
            df = pd.DataFrame(columns=categories)
            if not block.empty:
                if len(block) == batch_size:
                    d += 1
                    for j in range(len(datas)):
                        df.loc[datas[j]] = block[categories].iloc[j]
                        pbar.update(1)
                    dfs.append(df)
                else:
                    print("getting bad data at time", dates[d], dates[d+1], len(block))
            if d in chunks:
                output_df = pd.concat(dfs)
                output_df.index.name = 'date'
                output_df = output_df.reset_index()
                output_df.to_csv(f"{folder_path}/dataset_num_"+str(int(d/1000))+".csv")
                output_df = output_df.iloc[0:0]
                dfs = []
        if d not in chunks:
            output_df = pd.concat(dfs)
            output_df.index.name = 'date'
            output_df = output_df.reset_index()
            output_df.to_csv(f"{folder_path}/dataset_num_"+str(d//1000 + 1)+".csv")
