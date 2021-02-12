from binance.client import Client
from finta import TA
from datetime import datetime, date
import time as t
import creds # Binance API key
import ticker_list2 # List of all tickers on binance. 
import pandas as pd
import numpy as np
import datetime
import tweepy
import mplfinance as mpf

# Set up binance API
api_key = creds.APIkey
api_secret = creds.SecretKey
client = Client(api_key, api_secret)

# Set up tweepy API
auth = tweepy.OAuthHandler(creds.consumer_key, creds.consumer_secret)
auth.set_access_token(creds.access_token, creds.access_token_secret)
api = tweepy.API(auth)

while True:

    #Lists to hold values for creating database
    open_val = []
    high_val = []
    low_val = []
    close_val = []
    time_val = []                                                         
    pandasdti = []

    for kline in client.get_historical_klines_generator("BTCUSDT", Client.KLINE_INTERVAL_4HOUR, "1 months ago UTC"):
        
        #Code that converts unix timestamp to readable output
        timestamp = kline[0] #UTC time code
        timestamp = timestamp / 1000 #divides by 1000 because timestamp expects time in seconds but it comes in milliseconds and was giving the wrong date
        timestamp = datetime.datetime.fromtimestamp(timestamp).strftime('%Y-%m-%d %H:%M')
        time_val.append(timestamp)

        # converts unix time code to pandas DatetimeIndex object
        datetimee = pd.to_datetime(timestamp) 
        pandasdti.append(datetimee)

        #Adds ohlc values to lists
        open_val.append(float(kline[1]))
        high_val.append(float(kline[2]))
        low_val.append(float(kline[3]))
        close_val.append(float(kline[4]))
        

    # Combines ohlc value lists into one object then creates a pandas dataframe with that data.
    zippedList = list(zip(open_val, high_val, low_val, close_val))
    df = pd.DataFrame(zippedList, columns = ['open' , 'high', 'low', 'close'])

    # Creates second set of data for plotting it has to be formatted differently with a pandas datetimeindex object
    zippedList2 = list(zip(pandasdti, open_val, high_val, low_val, close_val))
    df2 = pd.DataFrame(zippedList2, columns = ['datetime', 'open' , 'high', 'low', 'close'])
    df2 = df2.set_index(['datetime'])

    # RSI indicator added to DF
    RSI = TA.RSI(df)
    df["RSI"] = RSI #Adds %b value column to df
    trade_signal = []

    for i in RSI:
        if i == 0:
            trade_signal.append(''),              
        elif i > 1:
            trade_signal.append(''),               
        elif i < 30:
            trade_signal.append('Oversold'),  
        elif i <= 1 and i >= 0:
            trade_signal.append('')

    #Adds trade column to df
    df['Trade'] = pd.DataFrame(trade_signal)

    # Format for console, prints dataframe
    pd.set_option('display.width', None)
    pd.set_option('display.max_rows', None)

    # Iterates through rows and looks for oversold RSI

    var = df['Trade'].tail(1)
    booly = var.str.contains('Oversold')
    price = df['close']

    # Prints last row in the df for the viewer to see
    print(df.tail(1))
    if booly[185] == True: #if the last rows trade signal is oversold tweet pic and chart
        print('a')
        tweet = f"PATHBOT\n$BTC #Bitcoin - {price[99]} - OVERSOLD\n\nPATHBOT"
        mpf.plot(df, type='candle', title = "PathBot BTCUSD 4h", datetime_format=' %A, %d-%m-%Y', tight_layout=True, savefig='upload.png')
        picpath = 'upload.png'
        api.update_with_media(picpath,tweet)
    t.sleep(3600) #Scans the 4h chart every 1 hour 




