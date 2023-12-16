import sys

from db_file import Database
import pandas as pd
import datetime as dt
import time


def getData(timeframe, col, client):
    symbol = "BTCUSDT"
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


def get_period_data(lastData, db):
    tic = time.time()  # Record start time
    col = list(lastData.columns)
    lastTime = dt.datetime.strptime(db["lastTime"], '%H:%M:%S.%f')
    if (lastTime + dt.timedelta(minutes=1)).strftime("%H:%M") == dt.datetime.now().strftime("%H:%M"):
        db["lastTime"] = str(dt.datetime.now().strftime('%H:%M:%S.%f'))
        d = getData(2, col)
        lastData = lastData.drop([lastData.index[0], lastData.index[len(lastData) - 1]])
        lastData = pd.concat([lastData, d])
    else:
        lastData = lastData.drop([lastData.index[len(lastData) - 1]])
        d = getData(1, col)
        lastData = pd.concat([lastData, d])
    toc = time.time()  # Record end time
    elapsed_time = toc - tic  # Calculate elapsed time
    return elapsed_time, lastData


def get_current_price():
    # return client.get_symbol_ticker(symbol="BTCUSDT")["price"]
    return None


class Backtesting:
    def __init__(self, file_path):
        # Load the DataFrame from the specified CSV file with 'date' as index
        self.df = pd.read_csv(file_path)

        # Initialize tick to 0
        self.tick = 60 * 30

        # print("Extimated time = " + str(len(self.df) / 100 * 13 / 60) + " minutes")

    def get_data(self, N, col):

        # Check if there is enough data
        if self.tick >= len(self.df):
            print("Insufficient data for the given N.")
            sys.exit()

        output_df = pd.DataFrame(columns=col)
        i = self.tick
        n = 1
        while n < N:
            while self.df["date"].iloc[i][17:19] != "59":
                i -= 1
            output_df.loc[self.df["date"].iloc[i]] = self.df[col].iloc[i]
            n += 1
            i -= 59
        self.tick += 1
        output_df = output_df[::-1]
        output_df = output_df.iloc[-N:]
        output_df.loc[self.df["date"].iloc[self.tick]] = self.df[col].iloc[self.tick]
        # print("   tick" + str(self.tick) + " out of " + str(len(self.df)))
        return output_df
