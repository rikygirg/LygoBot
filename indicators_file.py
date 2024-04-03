import re
import sys

import numpy as np


def _media(U, D, mode="normal"):
    if mode == "normal":
        _avgU = U.mean()
        _avgD = D.mean()
    elif mode == "exp":
        # print(U)
        U = U.ewm(span=6, adjust=False)
        D = D.ewm(span=6, adjust=False)
        # print(U)
        U = U.mean()
        D = D.mean()
        # print(U)
        _avgU = U.mean()
        _avgD = D.mean()
    else:
        _avgU = 0.00
        _avgD = 0.00
    return _avgU.iloc[0], _avgD.iloc[0]


def RSI(data, db, period=6, mode="normal"):
    data = data[["close"]]
    U = data.diff()
    U[U < 0] = 0
    D = data.diff()
    D[D > 0] = 0
    D = D.abs()
    # D = down difference in abs, U = up difference in abs
    U = U.drop(U.index[range(0, 24 - period + 1)])
    D = D.drop(D.index[range(0, 24 - period + 1)])
    AvgU, AvgD = _media(U, D, mode)
    if AvgD < 0.0001:
        RS = 99.999
    else:
        RS = AvgU / AvgD
    rsi_value = 100 - 100 / (1 + RS)
    # print(db)
    db[f"RSI{period}"] = rsi_value
    return rsi_value


def _ema_ricorsiva(data, alpha, ema_last):
    if len(data) == 1:
        #return data[0] * alpha + ema_last * (1 - alpha)
        return ema_last
    ema = data[0] * alpha + ema_last * (1 - alpha)
    return _ema_ricorsiva(data[1:], alpha, ema)


def EMA(data, db, period=12, alpha=None):
    period += 1
    data = data[["close"]].values
    if alpha is None:
        alpha = 2 / (period + 1)
    # ema_start = data[-period:].mean()
    ema_start = data[-period]
    ema_value = _ema_ricorsiva(data[-(period - 1):], alpha, ema_start)
    db[f"EMA{period}"] = float(ema_value)
    # print(f"\n ema{period}: {ema_value}")
    return float(ema_value)


'''
def Get_Indicator(input_string):
    pattern = r'(\w+)\((.*?)\)'
    match = re.match(pattern, input_string)
    if match is not None:
        name = match.group(1)
        arguments_str = match.group(2)
        arguments = [arg.replace(" ", "") for arg in arguments_str.split(',')]
        for i in range(len(arguments)):
            try:
                arguments[i] = float(arguments[i])
            except:
                pass
    else:
        print("Cannot identify indicator named: " + input_string)
        return None
    function = globals().get(name.upper())
    if function is not None and callable(function):
        return function, arguments
    else:
        print("Cannot find indicator named: " + name)
        return None
'''


class MeanRSI:
    def __init__(self, periods, less_than, value):
        self.periods = periods
        self.value = float(value)
        self.minor_sign = less_than

    def Check(self, data, db):
        rsi_array = np.array([RSI(data, db, period=i) for i in self.periods])
        rsi_mean = float(rsi_array.mean())
        return not ((rsi_mean <= self.value) ^ self.minor_sign)


class CrossingEMA:
    def __init__(self, periods, boundaries=[0.6, 0.85]):
        self.periods = periods
        self.boundaries = boundaries
        self.is_first_lower = True  # is EMA(12) > EMA(24)? True
        self.__is_first_iter = True
        self.__allowed_to_buy = True
        
    def Check(self, data, db):
        ema_array = np.array([EMA(data, db, period=i) for i in self.periods])
        if ema_array[0] - ema_array[1] > self.boundaries[0] * db["K_HEIGHT"] or ema_array[1] - ema_array[0] > self.boundaries[1] * db["K_HEIGHT"]:
            self.__allowed_to_buy = True
        db["Can Buy"] = self.__allowed_to_buy 
        if self.__is_first_iter:
            self.is_first_lower = ema_array[0] < ema_array[1]
            self.__is_first_iter = False
        if self.is_first_lower and ema_array[0] >= ema_array[1]:
            self.is_first_lower = False
            result = self.__allowed_to_buy
            self.__allowed_to_buy = False
            return result
        elif (not self.is_first_lower) and ema_array[0] < ema_array[1]:
            self.is_first_lower = True
            self.__allowed_to_buy = False
        return False


class CandlesHeight:
    def __init__(self, period=6, mode="MEAN"):
        self.period = period
        self.mode = mode

    def Check(self, data, db):
        high = data["close"][-(self.period + 2):-2].to_numpy()
        low = data["close"][-(self.period + 1):-1].to_numpy()
        candle_height = high - low
        db["K_HEIGHT"] = np.mean(abs(candle_height))
        return True
