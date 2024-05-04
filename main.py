import datetime as dt
import sys
import time
from binance import Client
import data_getter
from db_file import Database
from functions_file import ExitMargin, Logger, save_data, move_json
from path_manager import PathManager
from strategy_class import Strategy
from wallets_manager import Wallet, RealWallet
from indicators_file import CandlesHeight, CrossingEMA
from bot_class import Bot

db = Database('data.json')
client = Client(db['api_key'], db['api_secret'])
CURRENCY = "BTCFDUSD"
LOCAL_TESTING_TRADING = True  # TRUE FOR TESTING
NUMERO_BOT = 1
logger = Logger(False)
file_name = "Wallet_" + str(dt.datetime.now())[:-5]
pm = PathManager()

def ora(h=1, m=0, s=0):
    orario = dt.datetime.now() + dt.timedelta(hours=h, minutes=m, seconds=s)
    orario = orario.strftime("%D:%H:%M:%S")
    return orario


if not LOCAL_TESTING_TRADING:
    wallets = [RealWallet(client, CURRENCY) for i in range(NUMERO_BOT)]
else:
    wallets = [Wallet(1000, fees={"buy": 0.00, "sell": 0.00}) for i in range(NUMERO_BOT)]


databases = [Database(f"db_bot{i}.json") for i in range(NUMERO_BOT)]
# strats = [Strategy(constraints_buy=[MeanRSI([6, 12, 24], less_than=True, value=32.5), CandlesHeight(),
#                                    MeanRSI([6, 12, 24], less_than=False, value=30)], 
strats = [Strategy(constraints_buy=[CrossingEMA(periods=[12, 24], 
                                                targets=[1, 20], 
                                                boundaries=[0.5, 0.6]), CandlesHeight()],
                   constraints_sell=[ExitMargin(take_profit=2.5,
                                                stop_loss=1.5, candle_based=True,
                                                database=databases[i])])
          for i in range(NUMERO_BOT)]
bots = [Bot(wallets[i], strats[i], databases[i], f"bot{i}") for i in range(NUMERO_BOT)]
entrata_attiva = [False for i in range(NUMERO_BOT)]

logger.PrintLine("Starting LygoBot")
logger.PrintLine("----------------")
for bot in range(len(bots)):
    logger.PrintLine("Starting balance: " + str(bots[bot].wallet.balanceUSD) + " bot " + str(bot) + " "  + ora())
    save_data(file_name, str(bots[bot].wallet.balanceUSD), pm.site_wallet)


while True:
    lastData = data_getter.getData(24 + 1, ["close", "volume", "high", "low", "qav"], client, CURRENCY)
    for bot in range(len(bots)):
        if not entrata_attiva[bot]:
            if bots[bot].wallet.balanceUSD < 1120.00 and not LOCAL_TESTING_TRADING:
                sys.exit()
            db["EMA(12-24)"] = db["EMA12"] - db["EMA24"]
            # db["RSI"] = MEAN(db["RSI6"], db["RSI12"], db["RSI24"])
            # logger.PrintInline("media RSI: " + str(MEAN(db["RSI6"], db["RSI12"], db["RSI24"])))
            logger.PrintInline("EMA(12): " + str(db["EMA12"]) + ", EMA(24): " + str(db["EMA24"])
                               + ", Diff = " + str(db["EMA12"] - db["EMA24"]))
            if bots[bot].Check_to_Buy(lastData, db):
                logger.PrintLine("\n" + ora() + "\nI JUST BOUGHT (bot_" + str(bot) + ") " + str(
                    bots[bot].wallet.balanceBTC) + " BTC at " + str(lastData.iloc[-1]["close"]) + " K_Height: " + str(
                    db["K_HEIGHT"]), reverse=True)
                entrata_attiva[bot] = True
            time.sleep(0.1)
        if entrata_attiva[bot]:
            if bots[bot].Check_to_Sell(lastData, db):
                logger.PrintLine(
                    "\n" + ora() + "\nI JUST SOLD (bot=" + str(bot) + ") all BTC at " + str(lastData.iloc[-1]["close"])
                    + "\nNet balance usd: " + str(bots[bot].wallet.balanceUSD), reverse=True)
                save_data(file_name, str(bots[bot].wallet.balanceUSD), pm.site_wallet)
                entrata_attiva[bot] = False
            time.sleep(0.1)
    move_json(pm.bot_folder + "/data.json", pm.site_json, ['api_key', 'api_secret', 'lastTime', 'qty_sell'])
