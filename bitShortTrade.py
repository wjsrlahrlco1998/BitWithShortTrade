import pyupbit
import time
import datetime
import numpy as np

access = ""
secret = ""

########################################################################

def get_best(ticker):
    best_ror = 0
    best_k = 0.5
    for k in np.arange(0.1, 1.0, 0.1):
        df = pyupbit.get_ohlcv(ticker, interval="minute3", count=10)
        df['range'] = (df['high'] - df['low']) * k
        df['target'] = df['open'] + df['range'].shift(1)

        df['ror'] = np.where(df['high'] > df['target'],
                             df['close'] / df['target'],
                             1)

        ror = df['ror'].cumprod()[-2]

        if best_ror < ror:
            best_ror = ror
            best_k = k

    return best_k, best_ror

def get_target_price(ticker, k):
    """변동성 돌파 전략으로 매수 목표가 조회"""
    df = pyupbit.get_ohlcv(ticker, interval="minute3", count=10)
    target_price = df.iloc[0]['close'] + (df.iloc[0]['high'] - df.iloc[0]['low']) * k
    return target_price

def get_balance(ticker):
    """잔고 조회"""
    balances = upbit.get_balances()
    for b in balances:
        if b['currency'] == ticker:
            if b['balance'] is not None:
                return float(b['balance'])
            else:
                return 0
    return 0

def get_current_price(ticker):
    """현재가 조회"""
    return pyupbit.get_orderbook(ticker=ticker)["orderbook_units"][0]["ask_price"]

def find_best(list):
    b_coin = ""
    b_ror = 0
    b_k = 0.5
    ror = 0
    k = 0.5
    for i in list:
        try:
            k, ror = get_best(i)
            if ror > b_ror:
                b_ror = ror
                b_coin = i
                b_k = k
        except Exception as e:
            print(e)
    return b_coin, b_k
########################################################################

#암호화폐 목록
list_coin = pyupbit.get_tickers(fiat="KRW")
# 상승장 판단
best_coin, best_k = find_best(list_coin)

# 자동매매(30분 주기)
now = datetime.datetime.now()
end = now + datetime.timedelta(minutes=30)

# 로그인
upbit = pyupbit.Upbit(access, secret)
print("Autotrade start")

while True:
    try:
        now = datetime.datetime.now()
        if now < end:
            target_price = get_target_price(best_coin, best_k)
            current_price = get_current_price(best_coin)
            print("Target Price : ", target_price)
            print("Current Price : ", current_price)
            if target_price < current_price:
                krw = get_balance("KRW")
                if krw > 5000:
                    upbit.buy_market_order(best_coin, krw*0.9995)
                    print("Buy : ", best_coin)
        else:
            btc = get_balance(best_coin[4:])
            if btc > (5000 / get_current_price(best_coin)):
                upbit.sell_market_order(best_coin, btc*0.9995)
                print("Sell : ", best_coin)
                end = now + datetime.timedelta(minutes=30)
                # 코인 재설정
                best_coin, best_k = find_best(list_coin)
                time.sleep(1)
    except Exception as e:
        print(e)
        time.sleep(1)
