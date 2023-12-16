class Wallet:
    def __init__(self, initialBalance=100, fees=None):
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

