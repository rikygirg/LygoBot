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


def EMA(U, D, avgs, alpha, period=6, i=1):
    if i == len(U):
        return avgs
    AvgUt = alpha * U.iloc[i] + (1 - alpha) * U.iloc[i - 1]
    AvgDt = alpha * D.iloc[i] + (1 - alpha) * D.iloc[i - 1]
    avgs.append((AvgUt, AvgDt))
    return EMA(U, D, avgs, alpha, period, i + 1)


def K_HEIGHT(data, db, period=6, mode="MEAN"):
    period = int(period)
    high = data["close"][-(period+2):-2].to_numpy()
    low = data["close"][-(period+1):-1].to_numpy()
    candle_height = high - low
    if mode == "MEAN":
        db["K_HEIGHT"] = np.mean(abs(candle_height))
        return True
    db["K_HEIGHT"] = np.mean(abs(candle_height))
    return True


def RSI(data, db, period=6, mode="normal"):
    data = data[["close"]]
    period = int(period)
    U = data.diff()
    U[U < 0] = 0
    D = data.diff()
    D[D > 0] = 0
    D = D.abs()
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
