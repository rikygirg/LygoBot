import re
import sys
from db_file import Database

db = Database('data.json')


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


def TP(data):
    diff = data.iloc[-1]["close"] - db["price_buy"]
    print(diff)
    return diff


def RSI(data, period=6, mode="normal"):
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
    return rsi_value


def Get_Indicator(input_string):
    pattern = r'(\w+)\(([\d.,\s]+)\)'
    match = re.match(pattern, input_string)
    if match is not None:
        name = match.group(1)
        arguments_str = match.group(2)
        arguments = [float(arg) for arg in arguments_str.split(',')]
    else:
        print("Cannot identify indicator named: " + input_string)
        return None
    function = globals().get(name.upper())
    if function is not None and callable(function):
        return function, arguments
    else:
        print("Cannot find indicator named: " + name)
        return None
