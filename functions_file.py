import numpy as np
import json
import sys
from datetime import datetime
import os
from path_manager import PathManager
pm = PathManager()

def move_json(start_path, end_path, keys_to_remove=[]):
    # Load JSON data from start_path
    with open(start_path, 'r') as file:
        data = json.load(file)
    
    # Remove specified keys
    for key in keys_to_remove:
        data.pop(key, None)
    
    # Save modified JSON to end_path
    filename = os.path.basename(start_path)
    output_path = os.path.join(end_path, filename)
    with open(output_path, 'w') as file:
        json.dump(data, file, indent=4)


def save_data(file_name, data, folder=os.getcwd(), reverse=False):
    current_time = datetime.now().strftime('%Y-%m-%d_%H-%M-%S')
    file_path = os.path.join(folder, file_name)

    if reverse:
        # Read existing data from the file
        existing_data = ""
        if os.path.exists(file_path):
            with open(file_path, 'r') as file:
                existing_data = file.read()

        # Write new data followed by existing data
        with open(file_path, 'w') as file:
            file.write(data)
            if existing_data:
                file.write("\n")  # Add a line break if existing data exists
                file.write(existing_data)
    else:
        with open(file_path, 'a') as file:
            if os.path.getsize(file_path) > 0:
                file.write("\n")  # Skip a line if the file is not empty
            file.write(str(data))


def Log(message):
    message = "\r" + message
    sys.stdout.write(message)
    sys.stdout.flush()


class Logger:
    def __init__(self, backtesting):
        self.file_name = "bots_data_" + str(datetime.now())[:-5]
        self.was_printing_inline = False
        self.backtesting = backtesting

    def PrintLine(self, message, reverse=False):
        save_data(self.file_name, message, pm.site_logs, reverse)
        if self.was_printing_inline:
            self.was_printing_inline = False
            print()
        print(message)

    def PrintInline(self, message):
        Log(str(message))


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
    def __init__(self, stop_loss, take_profit, variable_in_percentage=False, candle_based=False, database=None, log=True):
        self.offsetDown = None
        self.offsetUp = None
        self.stop_loss = stop_loss
        self.take_profit = take_profit
        self.variable_in_percentage = variable_in_percentage
        self.candle_based = candle_based
        self.bot_db = database
        self.flag = False
        self.log = log

    def Check(self, data, db):
        if self.candle_based and not self.flag:
            self.flag = True
            self.offsetUp = float(db["K_HEIGHT"]) * self.take_profit
            self.offsetDown = float(db["K_HEIGHT"]) * self.stop_loss
        if not self.candle_based:
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
            if self.log:
                Log(message)
            if condition:
                self.flag = False
        return condition


def MEAN(*args):
    if not args:
        return None
    array = np.array(args)
    mean = float(np.mean(array))
    # Log(str(round(mean, 4)))
    return mean

