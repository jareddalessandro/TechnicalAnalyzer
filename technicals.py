import numpy as np
from numpy import datetime64
from talib import stream
from talib.abstract import *
import pandas as pd
import datetime as dt

############ INDICATOR Wrapper Functions ##############
# Note: Don't use TA.stream feature as it was returning same data for ema/ma/sma
# Most of these technical functions returns an array of data, one value for each candle, however we just want the most recent value.

def get_rsi(data, period=14):
    rsi_field = RSI(data, period)
    return round(rsi_field[len(rsi_field)-1], 3)

def get_ema_9(data):
    ema_9 = EMA(data['close'], 9)
    return round(ema_9[len(ema_9)-1], 3)

def get_ema_21(data):
    ema_21 = EMA(data['close'], 21)
    return round(ema_21[len(ema_21)-1], 3)

def get_ema_50(data):
    ema_50 = EMA(data['close'], 50)
    return round(ema_50[len(ema_50)-1], 3)
    
def get_ema_120(data):
    ema_120 = EMA(data['close'], 120)
    return round(ema_120[len(ema_120)-1], 3)

def get_ema_200(data):
    ema_200 = EMA(data['close'], 200)
    return round(ema_200[len(ema_200)-1], 3)

def get_ma_9(data):
    ma_9 = MA(data['close'], 9)
    return round(ema_9[len(ma_9)-1], 3)

def get_ma_50(data):
    ma_50 = MA(data['close'], 50)
    return round(ma_50[len(ma_50)-1], 3)

def get_ma_120(data):
    ma_120 = MA(data['close'], 120)
    return round(ma_120[len(ma_120)-1], 3)

def get_ma_200(data):
    ma_200 = MA(data['close'], 200)
    return round(ma_200[len(ma_200)-1], 3)

def get_macd(data):
    macd, macdsignal, macdhist = MACD(data)
    return round(macd[len(macd)-1], 4), round(macdsignal[len(macd)-1], 4), round(macdhist[len(macd)-1], 4)

# Get Volume Weighted Average Price (VWAP) and Lower and Higher bands - two sigma lower and higher
# This isn't giving the same results as TV and webull, maybe due to the method to calculate STD   
def get_vwap(data):
    df = pd.DataFrame(data)
    df['Cum_Vol'] = df['volume'].cumsum()
    df['Cum_Vol_Price'] = (df['volume'] * (df['high'] + df['low'] + df['close'] ) / 3).cumsum()
    df['VWAP'] = df['Cum_Vol_Price'] / df['Cum_Vol']
    df['VWAP_High'] = df["VWAP"] + (df["VWAP"].std() * 2)  
    df['VWAP_Low'] = df["VWAP"] - (df["VWAP"].std() * 2)

    return round(df['VWAP'].iloc[-1], 3), round(df['VWAP_High'].iloc[-1], 3), round(df['VWAP_Low'].iloc[-1], 3)

        