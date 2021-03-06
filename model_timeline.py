import pymongo
import numpy as np 
from cryptoscraper import configure_db
import pandas as pd 
import matplotlib.pyplot as plt
import datetime as dt
import random
import ruptures as rpt



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

def plot_price_volume(from_date, to_date, df):
    price_arr = timeseries['price'].loc[from_date:to_date].values
    vol_arr = timeseries['volume'].loc[from_date:to_date].values
    timestamp_arr = timeseries.loc[from_date:to_date].index.values

    _, ax1 = plt.subplots(figsize=(15,6))
    ax1.plot(timestamp_arr, price_arr, 'b-')
    ax1.set_xlabel('timestamp')
    ax1.set_ylabel('price (high)', color='b')
    ax2 = ax1.twinx()
    ax2.plot(timestamp_arr, vol_arr, 'g-')
    ax2.set_ylabel('volume', color='g')
    plt.show()

def plot_change_points(df, label, from_date, to_date):
    signal = timeseries[label].loc[from_date:to_date].values
    timeline = df.loc[from_date:to_date].index

    algo = rpt.Pelt(model="rbf").fit(signal)
    result = algo.predict(pen=10)

    plt.plot(timeline, signal, 'b-')
    for xc in np.take(timeline, [x - 1 for x in result]):
        plt.axvline(x=xc, color='black', linestyle='--')

    plt.show()

def get_change_point_dates(df, label, from_date, to_date):
    signal = timeseries[label].loc[from_date:to_date].values
    timeline = df.loc[from_date:to_date].index

    algo = rpt.Pelt(model="rbf").fit(signal)
    result = algo.predict(pen=10)

    return np.take(timeline, [x - 1 for x in result])

# example call
timeseries = generate_timeseries("BTC")
# example plot of price and volume for given timespan
plot_price_volume("20161202", "20161210", timeseries)
# example plot of change points using PELT
plot_change_points(timeseries, 'price', "20161202", "20161210")
# example of retrieving change point dates
cp_dates = get_change_point_dates(timeseries, 'price', "20161202", "20161210")
