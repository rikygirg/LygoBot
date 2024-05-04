from data_getter import Backtester
from db_file import Database
from functions_file import ExitMargin
from strategy_class import Strategy
from wallets_manager import Wallet
from indicators_file import CandlesHeight, CrossingEMA
from bot_class import Bot
import pandas as pd



BALANCE_INIZIALE=1000.00
db = Database('data.json')
CURRENCY = "BTCFDUSD"
NUMERO_BOT = range(1)

wallets = [Wallet(BALANCE_INIZIALE, fees={"buy": 0.00, "sell": 0.00}) for i in NUMERO_BOT]
databases = [Database(f"db_bots/db_bot_bt{i}.json") for i in NUMERO_BOT]
strats = [Strategy(constraints_buy=[CrossingEMA([100, 200],
                                                [1, 20],
                                                [2.0, 2.0]),
                                    CandlesHeight(period=6)],
                constraints_sell=[ExitMargin(take_profit=0.0,
                                                stop_loss=0.0,
                                                candle_based=True,
                                                database=databases[i], log=False)])
        for i in NUMERO_BOT]
bots = [Bot(wallets[i], strats[i], databases[i], f"bot_bt{i}", leverage=1) for i in NUMERO_BOT]
entrata_attiva = [False for i in NUMERO_BOT]
balances = [[BALANCE_INIZIALE] for i in NUMERO_BOT]


bt = Backtester("periodoMerda", 202, max_index=1)
go = True
lastData = None
while go:
    lastData, go = bt.getData(200 + 2)
    if not go:
            break
    for bot in NUMERO_BOT:
        if not entrata_attiva[bot]:
            if bots[bot].Check_to_Buy(lastData, db):
                entrata_attiva[bot] = True
                bt.setCross()
                print(lastData.tail())
        else:
            if bots[bot].Check_to_Sell(lastData, db):
                bal = bots[bot].wallet.balanceUSD
                balances[bot].append(bal)
                entrata_attiva[bot] = False
bt.saveDf()
