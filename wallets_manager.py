import pandas as pd

def getWallet(client, currency):
    '''
    info = client.get_account()
    df = pd.DataFrame(info["balances"])
    df["free"] = df["free"].astype(float).round(4)
    df = df[df["free"] > 0]
    return df.iat[1, 1]
    '''
    info = client.get_account()
    asset = pd.DataFrame(info["balances"])["asset"]
    value = pd.DataFrame(info["balances"])["free"]
    for i in range(asset.size):
        if asset.at[i] == currency:
            return round(float(value.at[i]), 5)

class Wallet:
    def __init__(self, initialBalance=1000, fees=None):
        if fees is None:
            fees = {"buy": 0.00, "sell": 0.00}
        self.balanceUSD = initialBalance
        self.balanceBTC = 0.00
        self.fees = fees

    def buy(self, amountBTC, priceBTC):
        self.balanceUSD -= amountBTC * priceBTC
        self.balanceBTC += amountBTC * (1 - self.fees["buy"])

    def sell(self, amountBTC, priceBTC):
        self.balanceUSD += amountBTC * priceBTC * (1 - self.fees["sell"])
        self.balanceBTC -= amountBTC


class RealWallet:
    def __init__(self, client, CURRENCY):
        self.client = client
        self.CURRENCY = CURRENCY
        self.balanceUSD = getWallet(self.client, "FDUSD")  #DA SISTEMARE DINAMICAMENTE
        self.balanceBTC = getWallet(self.client, "BTC")

    def buy(self, amountBTC, priceBTC):
        order = self.client.order_market_buy(symbol=self.CURRENCY, quantity=amountBTC)
        self.balanceUSD = getWallet(self.client, "FDUSD")  #DA SISTEMARE DINAMICAMENTE
        self.balanceBTC = getWallet(self.client, "BTC")

    def sell(self, amountBTC, priceBTC):
        order = self.client.order_market_sell(symbol=self.CURRENCY, quantity=amountBTC)
        self.balanceUSD = getWallet(self.client, "FDUSD")  #DA SISTEMARE DINAMICAMENTE
        self.balanceBTC = getWallet(self.client, "BTC")

