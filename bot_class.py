class Bot:
    def __init__(self, w, strat, database, name, leverage=1):
        self.wallet = w
        self.strategy = strat
        self.db = database
        self.name = name
        self.leverage = leverage

    def Check_to_Buy(self, dati, db):
        (amountBTC, priceBTC) = self.strategy.Calculate_if_Buy(dati, self.wallet, self.db, db)
        if amountBTC:
            amountBTC = int(amountBTC * self.leverage * 1000)/1000.0
            self.wallet.buy(amountBTC, priceBTC)
            db["qty_sell"] = amountBTC
            return True
        return False

    def Check_to_Sell(self, dati, db):
        (amountBTC, priceBTC) = self.strategy.Calculate_if_Sell(dati, self.wallet, self.db, db)
        if amountBTC:
            amountBTC = int(amountBTC / self.leverage * 1000)/1000.0
            amountBTC = db["qty_sell"]  # CONTROLLARE SE BOT DIVERSI HANNO PORTAFOGLI
            self.wallet.sell(amountBTC, priceBTC)
            return True
        return False

