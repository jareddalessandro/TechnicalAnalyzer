# Version 0.9
# Finnhub API Documentation: https://finnhub.io/docs/api/quote
# TA-LIB Library https://github.com/mrjbq7/ta-lib
# Use Finnhub for pricing queries and TA-Lib for technicals
# For UTC timestamps: https://www.unixtimestamp.com/
# TODO:
    # Use Alpaca markets for testing. https://app.alpaca.markets/paper/dashboard/overview
    # Add logic for rejection or support holds
    # Add macd
    # add price correlation analysis for dxy/vix

from os import error
from socket import create_connection
from symtable import Symbol
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
import websocket
from jproperties import Properties
import os
import colorama
from colorama import Back, Fore, Style
import threading



# Load properties from config.properties
configs = Properties()
with open ('config.properties', 'rb') as config_file:
    configs.load(config_file)

colorama.init(autoreset=True)

def main():
    TEST_MODE = False
    FINNHUB_KEY = configs.get('FINNHUB_KEY').data
    SYMBOL = configs.get('SYMBOL').data
    user_defined_levels = []
    #user_defined_levels = get_user_defined_levels()


    client = finnhub.Client(api_key=FINNHUB_KEY)

    one_min_candles = None
    five_min_candles = None
    sixty_min_candles = None
    intra_day_min_candles = None
    counter = 1


    # Get current price using the websocket connection.
    websocket.enableTrace(False)
    ws = websocket.WebSocketApp(f"wss://ws.finnhub.io?token={FINNHUB_KEY}",
        on_open = on_open,
        on_message = on_message,
        on_error = on_error,        
        on_close = on_close)    
    
    # Run websocket on its own thread so it doesn't block the rest of the app
    wst = threading.Thread(target=ws.run_forever)
    wst.daemon
    wst.start()

    time.sleep(3)

    while True:
        now = int(time.time())
        #now = 1669394100

        market_open = get_market_open_time()

        previous_one_min = (now - 12060) # 201 mins in the past, which will pull 200 entries for 1 min
        previous_five_min = (now - 60060) # 5 x 201 mins, but it will not pull that many entries given the number of 5min entries per trading day is 300, 141 not including pm
        previous_sixty_min = (now - 1500060) # 60 x 60 x 200 seconds = will obtain 200 candles for hour data

        # Reset
        BULLISH_POINTS = 0
        BEARISH_POINTS = 0
        
        if (ws.cookie is None):
            print('There is an issue with the websocket connection. Sleeping...')
            time.sleep(5)
            continue
        else:
            current_price = float(ws.cookie)
        
        # Only run first time and every 20 iterations (basically 3 times a minute), this helps keep us within our API restrictions.
        if (counter == 1 or counter % 20 == 0):         
            counter += 1
            print('Polling...')
            # Get 201 candles for one min and get enough to do calculations for the rest of the time frames
            one_min_candles = client.stock_candles(symbol=SYMBOL, resolution=1, _from=previous_one_min, to=now)
            five_min_candles = client.stock_candles(symbol=SYMBOL, resolution=5, _from=previous_five_min, to=now)
            sixty_min_candles = client.stock_candles(symbol=SYMBOL, resolution=60, _from=previous_sixty_min, to=now)
            intra_day_min_candles = client.stock_candles(symbol=SYMBOL, resolution=1, _from=market_open, to=now)

            #current_price = 402.19

            if one_min_candles['s'] != 'ok' or five_min_candles['s'] != 'ok':
                print("ERROR: Houston we have a problem obtaining candle data from Finnhub.")
                time.sleep(5)
                continue
            else:
                print('------------------------------------------')
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
            sixty_min_data = {
                'open': np.array(sixty_min_candles['o']),
                'high': np.array(sixty_min_candles['h']),
                'low': np.array(sixty_min_candles['l']),
                'close': np.array(sixty_min_candles['c']),
                'volume': np.array(sixty_min_candles['v'])
            }
            intra_day_data = {
                'open': np.array(intra_day_min_candles['o']),
                'high': np.array(intra_day_min_candles['h']),
                'low': np.array(intra_day_min_candles['l']),
                'close': np.array(intra_day_min_candles['c']),
                'volume': np.array(intra_day_min_candles['v'])
            }



        analysis = ''
        # Analyze indicator values and set points        
        range_low_one_min, BULLISH_POINTS, BEARISH_POINTS, analysis = Analysis.analyze_range_low(one_min_data, current_price, BULLISH_POINTS, BEARISH_POINTS, analysis, 1.0)
        range_high_one_min, BULLISH_POINTS, BEARISH_POINTS, analysis = Analysis.analyze_range_high(one_min_data, current_price, BULLISH_POINTS, BEARISH_POINTS, analysis, 1.0)
        range_low_intraday, BULLISH_POINTS, BEARISH_POINTS, analysis = Analysis.analyze_range_low(intra_day_data, current_price, BULLISH_POINTS, BEARISH_POINTS, analysis, 1.2)
        range_high_intraday, BULLISH_POINTS, BEARISH_POINTS, analysis = Analysis.analyze_range_high(intra_day_data, current_price, BULLISH_POINTS, BEARISH_POINTS, analysis, 1.2)

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

        vwap, vwap_upper, vwap_lower, BULLISH_POINTS, BEARISH_POINTS, analysis = Analysis.analyze_vwap(intra_day_data, current_price, BULLISH_POINTS, BEARISH_POINTS, analysis, weight=2)
        
        if len(user_defined_levels):
            BULLISH_POINTS, BEARISH_POINTS, analysis = Analysis.analyze_user_defined_levels(user_defined_levels, one_min_data, current_price, BULLISH_POINTS, BEARISH_POINTS, analysis, weight=1.2)
            BULLISH_POINTS, BEARISH_POINTS, analysis = Analysis.analyze_user_defined_levels(user_defined_levels, five_min_data, current_price, BULLISH_POINTS, BEARISH_POINTS, analysis, weight=1.2)

        bearString = ' ' * int((50 + BEARISH_POINTS - BULLISH_POINTS))
        bullString = ' ' * int((50 + BULLISH_POINTS - BEARISH_POINTS))
        

        os.system('cls')
        print('TICKER:', SYMBOL)
        print(f"{Fore.YELLOW}CURRENT PRICE: {current_price}")
        print(f"{Fore.GREEN}BULL: {BULLISH_POINTS}")
        print(f"{Fore.RED}BEAR: {BEARISH_POINTS}")
        print(f"One_min_RSI ", one_min_rsi)
        print(f"Five_min_RSI ", five_min_rsi)
        print("One_min_ema_9 ", one_min_ema_9)
        print("One_min_ema_50 ", one_min_ema_50)
        print('one_min_ema_120', one_min_ema_120) 
        print('one_min_ema_200', one_min_ema_200)
        print("five_min_ema_9 ", five_min_ema_9)
        print("five_min_ema_50 ", five_min_ema_50)          
        print('five_min_ema_120', five_min_ema_120)                
        print('five_min_ema_200', five_min_ema_200)
        print('sixty min ema 50', sixty_min_ema_50)
        print('sixty min ema 120', sixty_min_ema_120)
        print('sixty min ema 200', sixty_min_ema_200)
        print('Range Low 1 min: ', range_low_one_min)
        print('Range High 1 min: ', range_high_one_min)
        print('Range Low Intraday: ', range_low_intraday)
        print('Range High Intraday: ', range_high_intraday)
        print('VWAP: ', vwap)
        print('VWAP Upper: ', vwap_upper)
        print('VWAP Lower: ', vwap_lower)
        print(analysis)
        print(f"{Fore.GREEN}{Back.GREEN}{bullString}" + f"{Fore.RED}{Back.RED}{bearString}")
        print(f"{Fore.GREEN}{Back.GREEN}{bullString}" + f"{Fore.RED}{Back.RED}{bearString}")
        print(f"{Fore.GREEN}{Back.GREEN}{bullString}" + f"{Fore.RED}{Back.RED}{bearString}")
        #print(len(five_min_data['close']))

        counter += 1
        time.sleep(1)
        
        


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


# Get the utc time value for market open, market open is configuable in config.properties 
def get_market_open_time():
    now = int(time.time())
    local = time.localtime(now)
    day = local.tm_mday
    year = local.tm_year
    month = local.tm_mon
    weekday = local.tm_wday
    yday = local.tm_yday
    t = (year, month, day, int(configs.get('MARKET_OPEN_HOUR').data), 30, 0, weekday, yday, 0)

    market_open_time = time.mktime(t)
    return (round(int(market_open_time),0))


# Parse the response to get the current price and then put that into the cookie variable (can't return from method)
def on_message(ws, message):    
    current_price = message.split('p":')
    current_price = current_price[1]
    current_price = current_price.split(',')
    current_price = current_price[0]
    ws.cookie = current_price
    

def on_error(ws, error):
    print(error)
    time.sleep(5)

def on_close(ws, message):
    print("### closed ###")
    
    

def on_open(ws):
    ws.send('{"type":"subscribe","symbol":"%s"}' %configs.get('SYMBOL').data)




if  __name__ == "__main__":
    main()