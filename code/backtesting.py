from data_getter import Backtester
from db_file import Database
from functions_file import ExitMargin
from strategy_class import Strategy
from wallets_manager import Wallet
from indicators_file import CandlesHeight, CrossingEMA
from bot_class import Bot
import pandas as pd
import time

BALANCE_INIZIALE=1000.00
p_df = pd.read_csv("Backtesting_1_12_feb24.csv")
db = Database('data.json')
CURRENCY = "BTCFDUSD"
NUMERO_BOT = range(1)
WRITING_CROSS = True
for j in [2,3]: #Quali file faccio?
    for i in NUMERO_BOT:
        print(
            f"Doing: {int(p_df.iloc[i]['EMA LOW'])}_{int(p_df.iloc[i]['EMA HIGH'])}_{p_df.iloc[i]['BOUNDARY UP']}_{p_df.iloc[i]['BOUNDARY LOW']}_{p_df.iloc[i]['TAKE PROFIT']}_{p_df.iloc[i]['STOP LOSS']}")
    time.sleep(0.1)
    bt = Backtester("dataNew", 202, cdf=j)

    wallets = [Wallet(BALANCE_INIZIALE, fees={"buy": 0.00, "sell": 0.00}) for i in NUMERO_BOT]
    databases = [Database(f"db_bots/db_bot_bt{i}.json") for i in NUMERO_BOT]
    strats = [Strategy(constraints_buy=[CrossingEMA([int(p_df.iloc[i]['EMA LOW']),
                                                    int(p_df.iloc[i]['EMA HIGH'])],
                                                    [1, 20],
                                                    [p_df.iloc[i]['BOUNDARY UP'],
                                                    p_df.iloc[i]['BOUNDARY LOW']]),
                                        CandlesHeight(period=6)],
                    constraints_sell=[ExitMargin(take_profit=p_df.iloc[i]['TAKE PROFIT'],
                                                    stop_loss=p_df.iloc[i]['STOP LOSS'],
                                                    candle_based=True,
                                                    database=databases[i], log=False)])
            for i in NUMERO_BOT]
    bots = [Bot(wallets[i], strats[i], databases[i], f"bot_bt{i}", leverage=1) for i in NUMERO_BOT]
    entrata_attiva = [False for i in NUMERO_BOT]
    go = True
    trades = [[] for i in NUMERO_BOT]
    balances = [[BALANCE_INIZIALE] for i in NUMERO_BOT]

    while go:
        # start_time = time.time()
        lastData, go = bt.getData(200 + 2)
        for bot in NUMERO_BOT:
            if not entrata_attiva[bot]:
                if not WRITING_CROSS:
                    if lastData.iloc[-1]['Cross'] == 1:
                        mess = str(lastData.index[-1]) + "   (Buy)"
                        trades[bot].append(mess)
                        entrata_attiva[bot] = True
                        print("\nI JUST BOUGHT (bot_" + str(bot) + ") " + str(
                            bots[bot].wallet.balanceBTC) + " BTC at " + str(lastData.iloc[-1]["close"]) + " K_Height: " + str(
                            db["K_HEIGHT"]))
                elif bots[bot].Check_to_Buy(lastData, db):
                    bt.setCross()
                    mess = str(lastData.index[-1]) + "   (Buy)"
                    trades[bot].append(mess)
                    entrata_attiva[bot] = True
                    print("\nI JUST BOUGHT (bot_" + str(bot) + ") " + str(
                        bots[bot].wallet.balanceBTC) + " BTC at " + str(lastData.iloc[-1]["close"]) + " K_Height: " + str(
                        db["K_HEIGHT"]))
            if entrata_attiva[bot]:
                if bots[bot].Check_to_Sell(lastData, db):
                    bal = bots[bot].wallet.balanceUSD
                    mess = str(lastData.index[-1]) + "    " + str(bal)
                    trades[bot].append(mess)
                    balances[bot].append(bal)
                    entrata_attiva[bot] = False
                    print("\nI JUST SOLD (bot=" + str(bot) + ") all BTC at " + str(lastData.iloc[-1]["close"])
                        + "\nNet balance usd: " + str(bots[bot].wallet.balanceUSD))
                    # print(mess, end="\r", flush=True)
        # end_time = time.time()
        # elapsed_time = end_time - start_time
        # print(elapsed_time)

    bt.saveDf()
    print("Saving files...")

    for i in NUMERO_BOT:
        p_df.loc[i, "PROFIT"] = balances[i][-1]
        with open(
                f"tradeHistory/trades_{int(p_df.iloc[i]['EMA LOW'])}_{int(p_df.iloc[i]['EMA HIGH'])}_{p_df.iloc[i]['BOUNDARY UP']}_{p_df.iloc[i]['BOUNDARY LOW']}_{p_df.iloc[i]['TAKE PROFIT']}_{p_df.iloc[i]['STOP LOSS']}_{bot}.txt",
                'w') as file:
            for j in trades[i]:
                file.write(f"{j}\n")

    p_df.to_csv("Backtesting_1_12_feb24.csv", index=False)
