import numpy as np
import sys


def Log(message):
    message = "\r" + message
    sys.stdout.write(message)
    sys.stdout.flush()


class SingleParameter:
    def __init__(self, name, operator, value, offset=0):
        if name in ['open_time', 'open', 'high', 'low', 'close', 'volume', 'close_time',
                    'qav', 'num_trades', 'taker_base_vol', 'taker_quote_vol', 'ignore']:
            self.parameter = name
        else:
            self.parameter = None
            print("Error finding parameter", name)
        if operator == ">" or operator == ">=":
            self.operator = 1
        elif operator == "<" or operator == "<=":
            self.operator = -1
        elif operator == "=" or operator == "==":
            self.operator = 0
        else:
            self.operator = None
            print("Error finding operator", operator, "for parameter", name)
        self.value = value
        self.offset = offset

    def Check(self, data, db):
        if self.operator is None:
            return None
        if self.operator == 0:
            # PER UGUAGLIANZA CONTROLLO 1% DI DISTANZA!
            print("\n", abs(data.iloc[-1 - self.offset][self.parameter] - self.value), " <= ", 0.01 * self.value)
            if abs(data.iloc[-1 - self.offset][self.parameter] - self.value) <= 0.01 * self.value:
                return True
            else:
                return False
        else:
            print("\n", data.iloc[-1 - self.offset][self.parameter] * self.operator, " >= ", self.value * self.operator)
            if data.iloc[-1 - self.offset][self.parameter] * self.operator >= self.value * self.operator:
                return True
            else:
                return False


class ExitMargin:
    def __init__(self, stop_loss, take_profit, variable_in_percentage=False):
        self.stop_loss = stop_loss
        self.take_profit = take_profit
        self.variable_in_percentage = variable_in_percentage

    def Check(self, data, db):
        condition = False
        if self.variable_in_percentage:
            return condition
        else:
            price = data.iloc[-1]["close"]
            condition_tp = price >= db["price_buy"] + self.take_profit
            condition_sl = price <= db["price_buy"] - abs(self.stop_loss)
            condition = condition_tp or condition_sl
            message = str(price) + " tp: " + str(db["price_buy"] + self.take_profit) + " sl: " + str(
                db["price_buy"] - abs(self.stop_loss))
            Log(message)
        return condition


def MEAN(*args):
    if not args:
        return None
    array = np.array(args)
    mean = float(np.mean(array))
    Log(str(round(mean, 4)))
    return mean
