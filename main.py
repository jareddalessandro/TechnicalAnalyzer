# Finnhub API Documentation: https://finnhub.io/docs/api/quote

from os import error
import finnhub
import datetime
import csv
import time
import smtplib, ssl
from email.mime.multipart import MIMEMultipart
from email.mime.text import MIMEText

from numpy import datetime64

finnhub_key = 'c6j6kjaad3ieecomvqh0'
resolution = '5'
symbol = "SPY"

def main():
    now = int(time.time())
    previous = (now - 1500)
    print("Now:", now)
    print('Previous', previous)
    #finnhub_client = finnhub.Client(api_key="c6j6kjaad3ieecomvqh0")

    #print(finnhub_client.technical_indicator(symbol="AAPL", resolution='D', _from=1583098857, to=1584308457, indicator='rsi', indicator_fields={"timeperiod": 3}))

    client = finnhub.Client(api_key=finnhub_key)
    #rsi = client.technical_indicator(symbol="SPY", resolution='1', _from=1666378800, to=1666379100, indicator='rsi', indicator_fields={"timeperiod": 5})
    #rsi = client.technical_indicator(symbol="SPY", resolution='1', _from=1666378800, to=1666380300, indicator='rsi', indicator_fields={"timeperiod": 25})
    rsi = client.technical_indicator(symbol=symbol, resolution=resolution, _from=previous, to=now, indicator='macd', indicator_fields={"timeperiod": 25})
    print(rsi)




def get_rsi(ticker):
    client = finnhub.Client(api_key=finnhub_key)





































if  __name__ == "__main__":
    main()