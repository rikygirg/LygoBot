class Bot:
    def __init__(self, w, strat, database):
        self.wallet = w
        self.strategy = strat
        self.db = database

    def Check_to_Buy(self, dati, db):
        (amountBTC, priceBTC) = self.strategy.Calculate_if_Buy(dati, self.wallet, self.db, db)
        if amountBTC != 0.00:
            self.wallet.buy(amountBTC, priceBTC)
            return True
        return False

    def Check_to_Sell(self, dati, db):
        (amountBTC, priceBTC) = self.strategy.Calculate_if_Sell(dati, self.wallet, self.db, db)
        if amountBTC != 0.00:
            self.wallet.sell(amountBTC, priceBTC)
            return True
        return False
