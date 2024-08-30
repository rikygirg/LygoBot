from data_getter import Backtester
from db_file import Database
from functions_file import ExitMargin, save_data_to_csv, calculate_execution_time
from strategy_class import Strategy
from wallets_manager import Wallet
from indicators_file import CandlesHeight, CrossingEMA
from bot_class import Bot
import pandas as pd
import numpy as np
from scipy.optimize import minimize
from sklearn.preprocessing import StandardScaler
import cProfile
import sys

BALANCE_INIZIALE=1000.00
db = Database('data.json', persist=False)
CURRENCY = "BTCFDUSD"
NUMERO_BOT = range(1)
folderPath = "dataNew"

@calculate_execution_time
def function(x):
    print(f"Doing: {x[0]}  {x[1]}")
    #x[0] = Take profit
    #x[1] = Stop loss
    
    wallets = [Wallet(BALANCE_INIZIALE, fees={"buy": 0.00, "sell": 0.00}) for i in NUMERO_BOT]
    databases = [Database(f"db_bots/db_bot_bt{i}.json", persist=False) for i in NUMERO_BOT]
    strats = [Strategy(constraints_buy=[CrossingEMA([100, 200],
                                                    [1, 20],
                                                    [2.0, 2.0]),
                                        CandlesHeight(period=6)],
                    constraints_sell=[ExitMargin(take_profit=x[0],
                                                    stop_loss=x[1],
                                                    candle_based=True,
                                                    database=databases[i], log=False)])
            for i in NUMERO_BOT]
    bots = [Bot(wallets[i], strats[i], databases[i], f"bot_bt{i}", leverage=1) for i in NUMERO_BOT]
    entrata_attiva = [False for i in NUMERO_BOT]
    balances = [[BALANCE_INIZIALE] for i in NUMERO_BOT]

    bt = Backtester(folderPath, 202, max_index=3)
    go = True
    lastData = None
    while go:
        lastData, go = bt.getData(200 + 2)
        if not go:
            break
        for bot in NUMERO_BOT:
            if not entrata_attiva[bot]:
                #qui posso mettere una variabile cross così se il primo bot crossa pure gli altri lo fanno
                if bots[bot].Check_to_Buy(lastData, db, cross=False): # forceBuy = True
                    entrata_attiva[bot] = True
            else:
                if bots[bot].Check_to_Sell(lastData, db):
                    bal = bots[bot].wallet.balanceUSD
                    balances[bot].append(bal)
                    entrata_attiva[bot] = False
    print("Final balance:", balances[0][-1])
    save_data_to_csv(float(x[0]), float(x[1]), float(balances[0][-1]))
    return -balances[0][-1]

# Scale your inputs
scaler = StandardScaler()
x_initial = np.array([7.0, 4.0])  # Initial guesses
x_scaled = scaler.fit_transform(x_initial.reshape(-1, 1)).flatten()

# Define a wrapper function for the optimization that unscales the variables
def scaled_function(x_scaled):
    x_unscaled = scaler.inverse_transform(np.array(x_scaled).reshape(1, -1)).flatten()
    return function(x_unscaled)

#cProfile.runctx('function()', globals(), locals())
#sys.exit()
# Perform optimization with callback 
bounds = [(0, None)] * len(x_scaled)
result = minimize(scaled_function, x_scaled, method='BFGS', options={'disp': True, 'eps': 1e-1})

# Output the optimized results
optimized_x = scaler.inverse_transform(np.array(result.x).reshape(1, -1)).flatten()
print("Optimized variables:", optimized_x)