import pymongo
import numpy as np 
from cryptoscraper import configure_db
import pandas as pd 
import matplotlib.pyplot as plt
import datetime as dt



def query_database(coin):
    """ queries the crypto database for price and volume 
    :param coin: String, coin ticker as used in cryptoscraper
    :return: database cursor of specific coin sorted by timestamp
    """

    client = configure_db()
    coll = client.cryptoposts.crypto
    
    query = {}
    query["coin"] = coin
    coin_cursor = coll.find(query).sort('time')

    return coin_cursor

def build_timeline(cursor):
    """ function to build the timeseries
    :param cursor: MongoDB cursor to iterate over chronically sorted entries per coin
    :return: Pandas DataFrame timeseries columns price, volume and index of time
    """

    volume = []
    price = []
    timestamp_string = []
    timestamp = []

    for entry in cursor:
        volume.append(entry['volumefrom'])
        price.append(entry['high'])
        timestamp_string.append(dt.datetime.fromtimestamp(int(entry['time'])).strftime('%d.%m.%Y %H:%M:%S'))
        t = dt.datetime.fromtimestamp(int(entry['time']))
        timestamp.append(np.datetime64(t))

    timeseries = pd.DataFrame(data = {'volume' : volume , 'price' : price, 'timestamp_string' : timestamp_string }, index=timestamp)

    return timeseries
    

def generate_timeseries(coin):
    """ wrapper to generate time series for a specific coin
    :param coin: String, coin ticker
    :return: pandas DataFrame times series with columns price, volume and index of time
    """
    cursor = query_database(coin)
    timeseries = build_timeline(cursor)
    return timeseries



timeseries = generate_timeseries("BTC")