# Finnhub API Documentation: https://finnhub.io/docs/api/quote
# TAAIO API Documentation: https://taapi.io/documentation/integration/manually/ NOT USING RIGHT NOW BECAUSE NOT HIGH FREQUENCY ENOUGH AND POOR DOCUMENTATION AND DOESNT SEEM TO SUPPORT POST REQUESTS FOR BULK
# TA-LIB Library https://github.com/mrjbq7/ta-lib
# Use Finnhub for pricing queries and TA-Lib for technicals

from os import error
import finnhub
import datetime
import time
from email.mime.multipart import MIMEMultipart
from email.mime.text import MIMEText
import numpy as np
from numpy import datetime64
import pandas as pd
import talib
from talib import stream
from talib.abstract import *

finnhub_key = 'c6j6kjaad3ieecomvqh0'
taapi_key = 'eyJhbGciOiJIUzI1NiIsInR5cCI6IkpXVCJ9.eyJjbHVlIjoiNjM1ZjE2YjJmYzVhOGFkZmVjZGM3MDIxIiwiaWF0IjoxNjY3MTc2MTE0LCJleHAiOjMzMTcxNjQwMTE0fQ.eqSZQiL9eCyfw7oFnaG5QsfVjpkFpWkRPgDFn8krksY'
symbol = "SPY"

def main():
    now = int(time.time())
    previous = (now - 12060) # 201 mins in the past, which will pull 200 entries

    now = 1667244600
    previous = 1667232540 # 201 mins in the past, which will pull 200 entries
        # Alert: This will likely need to be different so we get 200 entries for all time frames

    client = finnhub.Client(api_key=finnhub_key)

    one_min_candles = client.stock_candles(symbol=symbol, resolution=1, _from=previous, to=now)
    five_min_candles = client.stock_candles(symbol=symbol, resolution=5, _from=previous, to=now)

    candle_count = len(one_min_candles['c']) # Get the count of how many candles we have

    if one_min_candles['s'] != 'ok' or five_min_candles['s'] != 'ok':
        print("ERROR: Houston we have a problem obtaining candle data from Finnhub.")
    else: 
        print("SUCCESS: Obtained candle data from Finnhub")
 

    # Create an np ndarray to be used by TA-LIB in OHLCV format
    one_min_data = {
        'open': np.array(one_min_candles['o']),
        'high': np.array(one_min_candles['h']),
        'low': np.array(one_min_candles['l']),
        'close': np.array(one_min_candles['c']),
        'volume': np.array(one_min_candles['v'])
    }
    five_min_data = {
        'open': np.array(five_min_candles['o']),
        'high': np.array(five_min_candles['h']),
        'low': np.array(five_min_candles['l']),
        'close': np.array(five_min_candles['c']),
        'volume': np.array(five_min_candles['v'])
    }

   
    one_min_rsi = get_rsi(one_min_data)
    five_min_rsi = get_rsi(five_min_data)

    one_min_ma_200 = get_ma_200(one_min_data)
    one_min_ma_120 = get_ma_120(one_min_data)
    one_min_ma_50 = get_ma_50(one_min_data)

    five_min_ma_200 = get_ma_200(five_min_data)
    five_min_ma_120 = get_ma_120(five_min_data)
    five_min_ma_50 = get_ma_50(five_min_data)
    
    one_min_ema_200 = get_ema_200(one_min_data)
    one_min_ema_120 = get_ema_120(one_min_data)
    one_min_ema_50 = get_ema_50(one_min_data)
    one_min_ema_9 = get_ema_9(one_min_data)
    
    five_min_ema_200 = get_ema_200(five_min_data)
    five_min_ema_120 = get_ema_120(five_min_data)
    five_min_ema_50 = get_ema_50(five_min_data)
    five_min_ema_9 = get_ema_9(five_min_data)

    macd, macdsignal, macdhist = get_macd(one_min_data)
    
    print('\n')
    print(macd, macdsignal, macdhist)




############ INDICATOR Wrapper Functions ##############
# Note: Don't use stream feature as it was returning same data for ema/ma/sma


def get_rsi(data, period=14):
    rsi_field = RSI(data, period)
    return rsi_field[len(rsi_field)-1]

def get_ema_9(data):
    ema_9 = EMA(data['close'], 9)
    return ema_9[len(ema_9)-1]

def get_ema_50(data):
    ema_50 = EMA(data['close'], 50)
    return ema_50[len(ema_50)-1]
    
def get_ema_120(data):
    ema_120 = EMA(data['close'], 120)
    return ema_120[len(ema_120)-1]

def get_ema_200(data):
    ema_200 = EMA(data['close'], 200)
    return ema_200[len(ema_200)-1]

def get_ma_9(data):
    ma_9 = MA(data['close'], 9)
    return ema_9[len(ma_9)-1]

def get_ma_50(data):
    ma_50 = MA(data['close'], 50)
    return ma_50[len(ma_50)-1]

def get_ma_120(data):
    ma_120 = MA(data['close'], 120)
    return ma_120[len(ma_120)-1]

def get_ma_200(data):
    ma_200 = MA(data['close'], 200)
    return ma_200[len(ma_200)-1]

def get_macd(data):
    macd, macdsignal, macdhist = MACD(data)
    return round(macd[len(macd)-1], 4), round(macdsignal[len(macd)-1], 4), round(macdhist[len(macd)-1], 4)

























if  __name__ == "__main__":
    main()