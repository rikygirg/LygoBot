class Bot:
    def __init__(self, w, strat):
        self.wallet = w
        self.strategy = strat

    def Check_to_Buy(self, dati):
        (amountBTC, priceBTC) = self.strategy.Calculate_if_Buy(dati, self.wallet)
        if amountBTC != 0.00:
            self.wallet.buy(amountBTC, priceBTC)
            return True
        return False

    def Check_to_Sell(self, dati):
        (amountBTC, priceBTC) = self.strategy.Calculate_if_Sell(dati, self.wallet)
        if amountBTC != 0.00:
            self.wallet.sell(amountBTC, priceBTC)
            return True
        return False
