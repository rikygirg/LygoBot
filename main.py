import time
from wallets_manager import Wallet
from bot_class import Bot
from strategy_class import Strategy
from functions_file import ExitMargin, SingleParameter, Logger, MEAN
from db_file import Database
from binance import Client
import data_getter
import datetime as dt
import sys

db = Database('data.json')
client = Client(db['api_key'], db['api_secret'])
LOCAL_TESTING_TRADING = True
BACKTESTING = False
if BACKTESTING:
    backTester = data_getter.Backtesting("data1/")
NUMERO_BOT = 1
logger = Logger(BACKTESTING)

# LEGENDA:
# SingleParameter(name="volume", operator=">=", value=1)
# ExitMargin(take_profit=300, stop_loss=200)
if LOCAL_TESTING_TRADING:
    # creo bots:
    databases = [Database(f"db_bot{i}.json") for i in range(NUMERO_BOT)]
    wallets = [Wallet(1000, fees={"buy": 0.00, "sell": 0.00}) for i in range(NUMERO_BOT)]
    strats = [Strategy(indicators=["RSI(6)", "RSI(12)", "RSI(24)", "K_HEIGHT(6, MEAN)"],
                       constraints_buy=["mean(RSI(6), RSI(12), RSI(24)) <= 50", "K_HEIGHT(6, MEAN)"],
                       constraints_sell=["K_HEIGHT(6, MEAN)", ExitMargin(take_profit=2,
                                                                         stop_loss=1, dynamic=True,
                                                                         database=databases[i])]) for i in range(NUMERO_BOT)]
    bots = [Bot(wallets[i], strats[i], databases[i], f"bot{i}") for i in range(NUMERO_BOT)]


######### TO DO ##########
# 1) indicatore di altezza candele precedenti (media, max, exponential)  (DONE)
# 2) decidere sl tp precentuale
# 3) classe che salva su db una variabile runnando codice  (DONE)
# NUOVA STRATEGIA
# 1) ema12, ema24
# 2) comprare: cross 12 > 24
# 3) vendita: cross 12 < 24 or rsi(6) >< qualche valore or tp_sl_dinamico
# LOGGER
def ora(h=0, m=0, s=0):
    orario = dt.datetime.now() + dt.timedelta(hours=h, minutes=m, seconds=s)
    orario = orario.strftime("%D:%H:%M:%S")
    return orario


print("Starting LygoBot")
print("----------------")
for bot in range(len(bots)):
    print("Starting balance:", bots[bot].wallet.balanceUSD, "bot", bot)
currency = "BTCTUSD"

entrata_attiva = [False for i in range(NUMERO_BOT)]
data_to_update = [True for i in range(NUMERO_BOT)]

while True:
    # RACCOGLIAMO I DATI
    if BACKTESTING:
        lastData = backTester.get_data(N=24 + 1, col=["close", "volume", "high", "low", "qav"])
    else:
        if data_to_update[bot]:
            lastData = data_getter.getData(24 + 1, ["close", "volume", "high", "low", "qav"], client)
        t, lastData = data_getter.get_period_data(lastData, db, client)
        data_to_update[bot] = False
    for bot in range(len(bots)):
        if not entrata_attiva[bot]:
            logger.PrintInline(MEAN(db["RSI6"], db["RSI12"], db["RSI24"]))
            if bots[bot].Check_to_Buy(lastData, db):
                logger.PrintLine("\n" + ora() + "\nI JUST BOUGHT (bot_" + str(bot) + ") " + str(
                    bots[bot].wallet.balanceBTC) + " BTC at " + str(lastData.iloc[-1]["close"]))
                entrata_attiva[bot] = True
            if not BACKTESTING:
                time.sleep(0.1)
        if entrata_attiva[bot]:
            if bots[bot].Check_to_Sell(lastData, db):
                logger.PrintLine(
                    "\n" + ora() + "\nI JUST SOLD (bot=" + str(bot) + ") all BTC at " + str(lastData.iloc[-1]["close"]))
                print("Net balance usd: ", bots[bot].wallet.balanceUSD)
                data_to_update[bot] = True
                entrata_attiva[bot] = False
            if not BACKTESTING:
                time.sleep(0.1)
