import pyupbit
import pandas
import datetime
import time

# Trading Coin List
coinlist = ["KRW-BTC", "KRW-ETH", "KRW-ETC", "KRW-QTUM", "KRW-XRP", "KRW-XTZ"]
lower28 = [False, False, False, False, False, False]
higher70 = [True, True, True, True, True, True]

# RSI Calculater
def rsi(ohlc: pandas.DataFrame, period: int = 14):
    delta = ohlc["close"].diff()
    ups, downs = delta.copy(), delta.copy()
    ups[ups < 0] = 0
    downs[downs > 0] = 0

    AU = ups.ewm(com=period - 1, min_periods=period).mean()
    AD = downs.abs().ewm(com=period - 1, min_periods=period).mean()
    RS = AU / AD

    return pandas.Series(100 - (100 / (1 + RS)), name="RSI")

# Buy function(Market Price)
def buy(coin):
    money = upbit.get_balance("KRW")
    if money < 20000:
        res = upbit.buy_market_order(coin, money)
    elif money < 50000:
        res = upbit.buy_market_order(coin, money * 0.4)
    elif money < 100000:
        res = upbit.buy_market_order(coin, money * 0.3)
    else:
        res = upbit.buy_market_order(coin, money * 0.2)
    return

# Sell function(Market Price)
def sell(coin):
    amount = upbit.get_balance(coin)
    cur_price = pyupbit.get_current_price(coin)
    total = amount * cur_price
    if total < 20000:
        res = upbit.sell_market_order(coin, amount)
    elif total < 50000:
        res = upbit.sell_market_order(coin, amount * 0.4)
    elif total < 100000:
        res = upbit.sell_market_order(coin, amount * 0.3)
    else:
        res = upbit.sell_market_order(coin, amount * 0.2)
    return

# Start Code
access = ""
secret = ""
upbit = pyupbit.Upbit(access, secret)

# Auto Trade Code
while True:
    for i in range(0, len(coinlist), 1):
        data = pyupbit.get_ohlcv(ticker=coinlist[i], interval="minute3")
        now_rsi = rsi(data, 14).iloc[-1]
        # RSI -> HIGH = UPS, RSI -> LOW = DOWNS
        if now_rsi <= 28:
            lower28[i] = True
        elif now_rsi >= 33 and lower28[i] == True:
            buy(coinlist[i])
            lower28[i] = False
        elif now_rsi >= 70 and higher70[i] == False:
            sell(coinlist[i])
            higher70[i] = True
        elif now_rsi <= 60:
            higher70[i] = False
    time.sleep(0.5)
