import numpy as np
import sys
from indicators_file import K_HEIGHT


def Log(message):
    message = "\r" + message
    sys.stdout.write(message)
    sys.stdout.flush()


class Logger:
    def __init__(self):
        self.was_printing_continous = False

    def PrintLine(self, message):
        if self.was_printing_continous:
            print()
        print(message)

    def PrintContinous(self, message):
        print(message, end="/r")


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
    def __init__(self, stop_loss, take_profit, variable_in_percentage=False, dynamic=False, database=None):
        self.offsetDown = None
        self.offsetUp = None
        self.stop_loss = stop_loss
        self.take_profit = take_profit
        self.variable_in_percentage = variable_in_percentage
        self.dynamic = dynamic
        self.bot_db = database
        self.flag = False

    def Check(self, data, db):
        if self.dynamic and not self.flag:
            self.flag = True
            self.offsetUp = float(db["K_HEIGHT"]) * self.take_profit
            self.offsetDown = float(db["K_HEIGHT"]) * self.stop_loss
        if not self.dynamic:
            self.offsetUp = self.take_profit
            self.offsetDown = self.stop_loss

        # print(self.offsetUp, self.offsetDown)
        condition = False
        if self.variable_in_percentage:
            if condition:
                self.flag = False
            return condition
        else:
            price = data.iloc[-1]["close"]
            condition_tp = price >= self.bot_db["price_buy"] + self.offsetUp
            condition_sl = price <= self.bot_db["price_buy"] - abs(self.offsetDown)
            condition = condition_tp or condition_sl
            message = str(price) + " tp: " + str(self.bot_db["price_buy"] + self.offsetUp) + " sl: " + str(
                self.bot_db["price_buy"] - abs(self.offsetDown))
            Log(message)
            if condition:
                self.flag = False
        return condition


def MEAN(*args):
    if not args:
        return None
    array = np.array(args)
    mean = float(np.mean(array))
    Log(str(round(mean, 4)))
    return mean

