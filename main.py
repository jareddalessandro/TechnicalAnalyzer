# Finnhub API Documentation: https://finnhub.io/docs/api/quote
# TA-LIB Library https://github.com/mrjbq7/ta-lib
# Use Finnhub for pricing queries and TA-Lib for technicals
# For UTC timestamps: https://www.unixtimestamp.com/
# TODO:
    # Need to figure out math for approaching emas and rejecting emas
    # Maybe test using Alpaca markets. https://app.alpaca.markets/paper/dashboard/overview
    # add user defined levels
    # add price correlation analysis for dxy/vix

import websocket
from os import error
import finnhub
import datetime
import time
from email.mime.multipart import MIMEMultipart
from email.mime.text import MIMEText
import numpy as np
from numpy import datetime64
from talib import stream
from talib.abstract import *

finnhub_key = 'c6j6kjaad3ieecomvqh0'
symbol = "SPY"

buy_points = 0
sell_points = 0

def main():
    #now = int(time.time())
    #previous_one_min = (now - 12060) # 201 mins in the past, which will pull 200 entries for 1 min
    user_defined_levels = get_user_defined_levels()

    now = 1667417400
    previous_one_min = (now - 12060) # 201 mins in the past, which will pull 200 entries for 1 min
    previous_five_min = (now - 60000) # 5 x 201 mins in teh past, which will pull 200 entries for 5 min


    client = finnhub.Client(api_key=finnhub_key)

    while True:
        # Reset point counters
        buy_points = 0
        sell_points = 0
        one_min_candles = None
        five_min_candles = None


        one_min_candles = client.stock_candles(symbol=symbol, resolution=1, _from=previous_one_min, to=now)
        five_min_candles = client.stock_candles(symbol=symbol, resolution=5, _from=previous_five_min, to=now)


        if one_min_candles['s'] != 'ok' or five_min_candles['s'] != 'ok':
            print("ERROR: Houston we have a problem obtaining candle data from Finnhub.")
        else:
            print('------------------------------------------')
            print("SUCCESS: Obtained candle data from Finnhub")

        candle_count = len(five_min_candles['c']) # Get the count of how many candles we have
        
        print('count: ', candle_count)
        print(five_min_candles)
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

        current_price = client.quote(symbol=symbol) # THIS IS NOT FAST, MAY REQUIRE WEBSOCKET, BUT MAY BE FAST ENOUGH FOR WHAT WE WANT
        current_price = current_price['c'] 

        

        #print(macd, macdsignal, macdhist)
        print('Current Price:', current_price)

        # Get indicator values and set points
        one_min_rsi, buy_points, sell_points = analyze_rsi(one_min_data, current_price, buy_points, sell_points)
        five_min_rsi, buy_points, sell_points = analyze_rsi(five_min_data, current_price, buy_points, sell_points, 1.2)
        
        
        print('One Min RSI:', one_min_rsi)
        print('Five Min RSI:', five_min_rsi)
        print("BUY: ", buy_points)
        print("SELL: ", sell_points)

        time.sleep(2)







############ INDICATOR Logic Functions ##############
# Each function will need to add points to either the buy or sell counter 
# Each function should take:
    # 'data' as an input, which will contain candle data in OHLCV format
    # buy_points as an input which will represent the growing quantity of buy indications seen
    # sell_points as an input will will represent the growing quantity of sell indications seen
    # weight, a modifier we can use to determine how crucial each specific usage of the function is

def analyze_rsi(data, current_price, buy_points, sell_points, weight=1):
    rsi = get_rsi(data)
    if (rsi > 68):
        sell_points += (5 * weight)
    elif (rsi < 32):
        buy_points += (5 * weight)
    return rsi, buy_points, sell_points

#approaching 50ema from below = increase sell
#approaching 50 ema from above = increase buy
#break through 50 ema from below = increase buy hard
#break through 50 ema from above = increase sell hard
# has touched? is above is below
def analyze_ema_50(data, current_price, buy_points, sell_points, weight=1):
    ema = get_ema_50(data)









# maybe create functions for is it close to line, did it reject, did it break, did it hold
############ Direction Behavior Helper Functions ##############
#def approaching_line(current_price, line):

def get_user_defined_levels():
    user_defined_levels = []
    print("Please enter all specfiic critical levels you would like the bot to monitor.")
    while True:
        level = (input())
        if len(level) < 1:
            break
        else:
            user_defined_levels.append(float(level))
    return user_defined_levels

def get_range_low(data):
    lowest_low = data['open'][0]
    lows = []
    lows = data['low']
    for i in range(len(lows)):
        if lows[i] <= lowest_low:
            lowest_low = lows[i]
    return lowest_low


def get_range_high(data):
    highest_high = data['open'][0]
    highs = []
    highs = data['high']
    for i in range(len(highs)):
        if highs[i] >= highest_high:
            highest_high = highs[i]
    return highest_high


############ INDICATOR Wrapper Functions ##############
# Note: Don't use stream feature as it was returning same data for ema/ma/sma

def get_rsi(data, period=14):
    rsi_field = RSI(data, period)
    return rsi_field[len(rsi_field)-1]

def get_ema_9(data):
    ema_9 = EMA(data['close'], 9)
    return ema_9[len(ema_9)-1]

def get_ema_21(data):
    ema_21 = EMA(data['close'], 21)
    return ema_21[len(ema_21)-1]

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