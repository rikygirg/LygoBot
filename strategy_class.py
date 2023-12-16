import traceback
from functions_file import MEAN
import indicators_file
import numpy as np
import sys

def Log(message):
    sys.stdout.write("\r" + message)
    sys.stdout.flush()


class Strategy:
    def __init__(self, indicators=None, constraints_buy=None, constraints_sell=None, perc=1):
        self.buy_constraints = np.array(constraints_buy)  # ["mean(rsi(6), rsi(12), rsi(24)) <= 12"]
        for i in range(len(self.buy_constraints)):
            if isinstance(self.buy_constraints[i], str):
                self.buy_constraints[i] = self.buy_constraints[i].upper().replace("DB", "db").replace("PRICE_BUY", "price_buy")
        self.sell_constraints = np.array(constraints_sell)  # ["tp" = 200, "sl" = 100]
        for i in range(len(self.sell_constraints)):
            if isinstance(self.sell_constraints[i], str):
                self.sell_constraints[i] = self.sell_constraints[i].upper().replace("DB", "db").replace("PRICE_BUY", "price_buy")
        self.percentualToBuy = perc
        self.qty = 0
        self.indicators = {}
        for ind in indicators:  # ["rsi(6)", "rsi(12)", "rsi(24)"]
            indicator_tuple = indicators_file.Get_Indicator(ind.upper())
            if indicator_tuple is not None:
                self.indicators[ind.upper()] = indicator_tuple

    def _replace_indicators(self, constraint, data, db):
        for name, (func, args) in self.indicators.items():
            placeholder = f"{name}"
            try:
                indicator_value = func(data, db, *args)
            except Exception as e:
                print(f"Error calculating indicator: {name}, {e}")
                traceback.print_exc()
                return None
            constraint = constraint.replace(placeholder, str(indicator_value))
        return constraint

    def _evaluate_constrains(self, data, cons, db):
        results = []
        mod_cons = []
        for constraint in cons:
            try:
                if isinstance(constraint, str):
                    modified_constraint = self._replace_indicators(constraint, data, db)
                    mod_cons.append(modified_constraint)
                    result = eval(modified_constraint)
                    # results.append((constraint, result))
                    if isinstance(result, bool):
                        results.append(result)
                    else:
                        print(f"Error evaluating constraint: {constraint}, it is not a Logic operation")
                        # traceback.print_exc(limit=2)
                        results.append(None)
                else:
                    results.append(constraint.Check(data, db))
            except Exception as e:
                print(f"Error evaluating constraint: {constraint}, {e}")
                # traceback.print_exc(limit=2)
                results.append(None)
        return results

    def Calculate_if_Buy(self, data, wallet, bot_db, db):
        bot_db["price_buy"] = data.iloc[-1]["close"]
        results = self._evaluate_constrains(data, self.buy_constraints, db)
        if all(results):
            self.qty = int(wallet.balanceUSD / data.iloc[-1]["close"] * self.percentualToBuy * 1000) / 1000.0
            bot_db["price_buy"] = data.iloc[-1]["close"]
            return self.qty, data.iloc[-1]["close"]
        return 0, data.iloc[-1]["close"]

    def Calculate_if_Sell(self, data, wallet, bot_db, db):
        results = self._evaluate_constrains(data, self.sell_constraints, db)
        if all(results):
            self.qty = wallet.balanceBTC
            return self.qty, data.iloc[-1]["close"]
        return 0, data.iloc[-1]["close"]