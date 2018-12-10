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
    coll = client.cryptoposts.cryptodata
    
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
    timestamp = []

    for entry in cursor:
        volume.append(entry['volumefrom'])
        price.append(entry['high'])
        timestamp.append(dt.datetime.fromtimestamp(int(entry['time'])).strftime('%d.%m.%Y %H:%M:%S'))

    timeseries = pd.DataFrame(data = {'volume' : volume , 'price' : price }, index=timestamp)

    return timeseries
    

def generate_timeseries(coin):
    """ wrapper to generate time series for a specific coin
    :param coin: String, coin ticker
    :return: pandas DataFrame times series with columns price, volume and index of time
    """
    cursor = query_database(coin)
    timeseries = build_timeline(cursor)
    return timeseries

def plot_price_volume(from, to, df):
    fig, ax1 = plt.subplots(figsize=(15,6))
    ax1.plot(timestamp_arr_sample, price_arr_sample, 'b-')
    ax1.set_xlabel('timestamp')
    ax1.set_ylabel('price (high)', color='b')
    ax2 = ax1.twinx()
    ax2.plot(timestamp_arr_sample, vol_arr_sample, 'g-')
    ax2.set_ylabel('volume', color='g')
    plt.xticks(random.sample(timestamp_arr_sample.tolist(), 10), rotation='vertical')
    plt.show()
# example call
timeseries = generate_timeseries("BTC")
print(timeseries)
