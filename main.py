import time
from wallets_manager import Wallet
from bot_class import Bot
from strategy_class import Strategy
from functions_file import ExitMargin, SingleParameter
from db_file import Database
import data_getter
import datetime as dt
import sys

db = Database('data.json')
LOCAL_TESTING_TRADING = True
NUMERO_BOT = 1

# LEGENDA:
# SingleParameter(name="volume", operator=">=", value=1)
# ExitMargin(take_profit=300, stop_loss=200)
if LOCAL_TESTING_TRADING:
    # creo bots:
    wallets = [Wallet(1000 * (i + 1), fees={"buy": 0.00, "sell": 0.00}) for i in range(NUMERO_BOT)]
    strats = [Strategy(indicators=["RSI(6)", "RSI(12)", "RSI(24)"],
                       constraints_buy=["mean(RSI(6), RSI(12), RSI(24)) <= 12"],
                       constraints_sell=[ExitMargin(take_profit=60, stop_loss=30)]) for i in range(NUMERO_BOT)]
    bots = [Bot(wallets[i], strats[i]) for i in range(NUMERO_BOT)]


######### TO DO ##########
# 1) indicatore di altezza candele precedenti (media, max, exponential)
# 2) decidere sl tp precentuale
# 3) classe che salva su db una variabile runnando codice
# NUOVA STRATEGIA
# 1) ema12, ema24
# 2) comprare: cross 12 > 24
# 3) vendita: cross 12 < 24 or rsi(6) >< qualche valore or tp_sl_dinamico

def ora(h=0, m=0, s=0):
    orario = dt.datetime.now() + dt.timedelta(hours=h, minutes=m, seconds=s)
    orario = orario.strftime("%D:%H:%M:%S")
    return orario


def Log(message):
    sys.stdout.write(message)
    sys.stdout.flush()


print("Starting LygoBot")
print("----------------")
for bot in range(len(bots)):
    print("Starting balance:", bots[bot].wallet.balanceUSD, "bot", bot)
currency = "BTCTUSD"

entrata_attiva = [False for i in range(NUMERO_BOT)]
data_to_update = [True for i in range(NUMERO_BOT)]

while True:
    # RACCOGLIAMO I DATI
    if data_to_update[bot]:
        lastData = data_getter.getData(24 + 1, ["close", "volume", "high", "low", "qav"])
    t, lastData = data_getter.get_period_data(lastData)
    data_to_update[bot] = False
    for bot in range(len(bots)):
        if not entrata_attiva[bot]:
            if bots[bot].Check_to_Buy(lastData):
                print("\n" + ora() + "\nI JUST BOUGHT (bot_" + str(bot) + ") " + str(
                    bots[bot].wallet.balanceBTC) + " BTC at " + str(lastData.iloc[-1]["close"]))
                entrata_attiva[bot] = True
            time.sleep(0.1)
        if entrata_attiva[bot]:
            if bots[bot].Check_to_Sell(lastData):
                print(
                    "\n" + ora() + "\nI JUST SOLD (bot=" + str(bot) + ") all BTC at " + str(lastData.iloc[-1]["close"]))
                print("Net balance usd: ", bots[bot].wallet.balanceUSD)
                data_to_update[bot] = True
                entrata_attiva[bot] = False
            time.sleep(0.1)
