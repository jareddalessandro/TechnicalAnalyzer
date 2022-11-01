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
from talib.abstract import *

finnhub_key = 'c6j6kjaad3ieecomvqh0'
taapi_key = 'eyJhbGciOiJIUzI1NiIsInR5cCI6IkpXVCJ9.eyJjbHVlIjoiNjM1ZjE2YjJmYzVhOGFkZmVjZGM3MDIxIiwiaWF0IjoxNjY3MTc2MTE0LCJleHAiOjMzMTcxNjQwMTE0fQ.eqSZQiL9eCyfw7oFnaG5QsfVjpkFpWkRPgDFn8krksY'
resolution = '1'
symbol = "SPY"

def main():
    now = int(time.time())
    previous = (now - 1860) # 31 mins in the past, which will pull 30 entries

    now = 1667244600
    previous = 1667242800


    #print("Now:", now)
    #print('Previous', previous)

    client = finnhub.Client(api_key=finnhub_key)

    finnhub_candles = client.stock_candles(symbol=symbol, resolution=resolution, _from=previous, to=now)
    candle_count = len(finnhub_candles['c']) # Get the count of how many candles we have

    if finnhub_candles['s'] != 'ok':
        print("ERROR: Houston we have a problem obtaining candle data from Finnhub.")
    else: 
        print("SUCCESS: Obtained candle data from Finnhub")
    
    # Digest the candle data into a list of dictionaries as required by TAAIO
    #candles = [{}]
    #for i in range(candle_count):
    #   
    #    dictionary = {
    #            'open': finnhub_candles['o'][i],
    #            'high': finnhub_candles['h'][i],
    #            'low': finnhub_candles['l'][i],
    #            'close': finnhub_candles['c'][i],
    #            'volume': finnhub_candles['v'][i]
    #        }
    #    candles.append(dictionary)
    #candles.pop(0) # remove the first entry which is an empty dictionary

  

    # Create an np ndarray to be used by TA-LIB in OHLCV format
    one_min_data = {
        'open': np.array(finnhub_candles['o']),
        'high': np.array(finnhub_candles['h']),
        'low': np.array(finnhub_candles['l']),
        'close': np.array(finnhub_candles['c']),
        'volume': np.array(finnhub_candles['v'])
    }

    print(one_min_data)
    
    #np_array = np.array(finnhub_candles['c'])
    #print(data)
    #np_array = np.array(finnhub_candles)
    # np_array = {'open': 'array'(finnhub_candles['o']), 'high': 'array'(finnhub_candles['h']), 'low': 'array'(finnhub_candles['l']), 'close': 'array'(finnhub_candles['c']), 'volume': tuple(finnhub_candles['v'])}
    #print(np_array)


    #SMA = abstract.SMA
    #RSI = abstract.RSI

    # This seems to be pretty accurate actually, it requires at least 14 increments of data
    rsi_field = RSI(one_min_data, timeperiod=14)
    ema_field = EMA(one_min_data)
    current_rsi = rsi_field[len(rsi_field)-1]
    
    print(ema_field)
    print(current_rsi)



































if  __name__ == "__main__":
    main()