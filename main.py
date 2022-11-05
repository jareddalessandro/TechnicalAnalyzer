# Finnhub API Documentation: https://finnhub.io/docs/api/quote
# TA-LIB Library https://github.com/mrjbq7/ta-lib
# Use Finnhub for pricing queries and TA-Lib for technicals
# For UTC timestamps: https://www.unixtimestamp.com/
# TODO:
    # Use Alpaca markets for testing. https://app.alpaca.markets/paper/dashboard/overview
    # Replace quote() for current_price with websocket
    # Add vwap and bands
    # Add logic for rejection or support holds
    # Add macd
    # add price correlation analysis for dxy/vix

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
import technicals as TA
import analyze as Analysis
import time

FINNHUB_KEY = 'c6j6kjaad3ieecomvqh0'
SYMBOL = "SPY"

def main():

    user_defined_levels = get_user_defined_levels()
    now = int(time.time())
    now = int('1667581200') # 11/4 1200am

    market_open = get_market_open_time()

    previous_one_min = (now - 12060) # 201 mins in the past, which will pull 200 entries for 1 min
    previous_five_min = (now - 600060) # 5 x 201 mins, but it will not pull that many entries given the number of 5min entries per trading day is 300, 141 not including pm
    previous_60_min = (now - 1500060) # 60 x 60 x 200 seconds = will obtain 200 candles for hour data

    client = finnhub.Client(api_key=FINNHUB_KEY)
    
    while True:
        # Reset point counters
        BULLISH_POINTS = 0
        BEARISH_POINTS = 0
        one_min_candles = None
        five_min_candles = None


        one_min_candles = client.stock_candles(symbol=SYMBOL, resolution=1, _from=previous_one_min, to=now)
        five_min_candles = client.stock_candles(symbol=SYMBOL, resolution=5, _from=previous_five_min, to=now)
        sixty_min_candles = client.stock_candles(symbol=SYMBOL, resolution=60, _from=previous_60_min, to=now)
        intra_day_min_candles = client.stock_candles(symbol=SYMBOL, resolution=1, _from=market_open, to=now)

        current_price = client.quote(symbol=SYMBOL) # THIS IS NOT FAST, MAY REQUIRE WEBSOCKET, BUT MAY BE FAST ENOUGH FOR WHAT WE WANT
        current_price = float(current_price['c'])
        current_price = 371.28

        print('Current Price:', current_price)

        if one_min_candles['s'] != 'ok' or five_min_candles['s'] != 'ok':
            print("ERROR: Houston we have a problem obtaining candle data from Finnhub.")
        else:
            print('------------------------------------------')
            print("SUCCESS: Obtained candle data from Finnhub")

        #candle_count = len(sixty_min_candles['c']) # Get the count of how many candles we have

        
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
        sixty_min_data = {
            'open': np.array(sixty_min_candles['o']),
            'high': np.array(sixty_min_candles['h']),
            'low': np.array(sixty_min_candles['l']),
            'close': np.array(sixty_min_candles['c']),
            'volume': np.array(sixty_min_candles['v'])
        }
        #intra_day_data = {
        #    'open': np.array(intra_day_min_candles['o']),
        #    'high': np.array(intra_day_min_candles['h']),
        #    'low': np.array(intra_day_min_candles['l']),
        #    'close': np.array(intra_day_min_candles['c']),
        #    'volume': np.array(intra_day_min_candles['v'])
        #}

        analysis = ''
        # Analyze indicator values and set points        
        one_range_low, BULLISH_POINTS, BEARISH_POINTS, analysis = Analysis.analyze_range_low(one_min_data, current_price, BULLISH_POINTS, BEARISH_POINTS, analysis, 1.2)
        one_range_high, BULLISH_POINTS, BEARISH_POINTS, analysis = Analysis.analyze_range_high(one_min_data, current_price, BULLISH_POINTS, BEARISH_POINTS, analysis, 1.2)

        one_min_rsi, BULLISH_POINTS, BEARISH_POINTS, analysis = Analysis.analyze_rsi(one_min_data, BULLISH_POINTS, BEARISH_POINTS, analysis)
        five_min_rsi, BULLISH_POINTS, BEARISH_POINTS, analysis = Analysis.analyze_rsi(five_min_data, BULLISH_POINTS, BEARISH_POINTS, analysis)

        one_min_ema_9, BULLISH_POINTS, BEARISH_POINTS, analysis = Analysis.analyze_ema_9(one_min_data, current_price, BULLISH_POINTS, BEARISH_POINTS, analysis, 1.0)
        five_min_ema_9, BULLISH_POINTS, BEARISH_POINTS, analysis = Analysis.analyze_ema_9(five_min_data, current_price, BULLISH_POINTS, BEARISH_POINTS, analysis, 1.2)

        one_min_ema_50, BULLISH_POINTS, BEARISH_POINTS, analysis = Analysis.analyze_ema_50(one_min_data, current_price, BULLISH_POINTS, BEARISH_POINTS, analysis)
        five_min_ema_50, BULLISH_POINTS, BEARISH_POINTS, analysis = Analysis.analyze_ema_50(five_min_data, current_price, BULLISH_POINTS, BEARISH_POINTS, analysis, 1.4)
        sixty_min_ema_50, BULLISH_POINTS, BEARISH_POINTS, analysis = Analysis.analyze_ema_50(sixty_min_data, current_price, BULLISH_POINTS, BEARISH_POINTS, analysis, 1.6)

        one_min_ema_120, BULLISH_POINTS, BEARISH_POINTS, analysis = Analysis.analyze_ema_120(one_min_data, current_price, BULLISH_POINTS, BEARISH_POINTS, analysis, 1.1)
        five_min_ema_120, BULLISH_POINTS, BEARISH_POINTS, analysis = Analysis.analyze_ema_120(five_min_data, current_price, BULLISH_POINTS, BEARISH_POINTS, analysis, 1.3)
        sixty_min_ema_120, BULLISH_POINTS, BEARISH_POINTS, analysis = Analysis.analyze_ema_120(sixty_min_data, current_price, BULLISH_POINTS, BEARISH_POINTS, analysis, 1.5)

        one_min_ema_200, BULLISH_POINTS, BEARISH_POINTS, analysis = Analysis.analyze_ema_200(one_min_data, current_price, BULLISH_POINTS, BEARISH_POINTS, analysis, 1.2)
        five_min_ema_200, BULLISH_POINTS, BEARISH_POINTS, analysis = Analysis.analyze_ema_200(five_min_data, current_price, BULLISH_POINTS, BEARISH_POINTS, analysis, 1.4)
        sixty_min_ema_200, BULLISH_POINTS, BEARISH_POINTS, analysis = Analysis.analyze_ema_200(sixty_min_data, current_price, BULLISH_POINTS, BEARISH_POINTS, analysis, 2)
        
        if len(user_defined_levels):
            BULLISH_POINTS, BEARISH_POINTS, analysis = Analysis.analyze_user_defined_levels(user_defined_levels, one_min_data, current_price, BULLISH_POINTS, BEARISH_POINTS, analysis, weight=1.2)
            BULLISH_POINTS, BEARISH_POINTS, analysis = Analysis.analyze_user_defined_levels(user_defined_levels, five_min_data, current_price, BULLISH_POINTS, BEARISH_POINTS, analysis, weight=1.2)
            
        
        print("BULL: ", BULLISH_POINTS)
        print("BEAR: ", BEARISH_POINTS)
        print("One_min_ema_9 ", one_min_ema_9)
        print("One_min_ema_50 ", one_min_ema_50)
        print("five_min_ema_9 ", five_min_ema_9)
        print("five_min_ema_50 ", five_min_ema_50)
        print('one_min_ema_120', one_min_ema_120)
        print('five_min_ema_120', five_min_ema_120)
        print('one_min_ema_200', one_min_ema_200)
        print('five_min_ema_200', five_min_ema_200)
        print('sixty min ema 50', sixty_min_ema_50)
        print('sixty min ema 120', sixty_min_ema_120)
        print('sixty min ema 200', sixty_min_ema_200)
        print(analysis)

        time.sleep(3)
        


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



def get_market_open_time():
    now = int(time.time())
    local = time.localtime(now)
    day = local.tm_mday
    year = local.tm_year
    month = local.tm_mon
    weekday = local.tm_wday
    yday = local.tm_yday
    t = (year, month, day, 6, 30, 0, weekday, yday, 0)

    market_open_time = time.mktime(t)
    return (round(int(market_open_time),0))


if  __name__ == "__main__":
    main()