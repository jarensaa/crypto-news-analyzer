import pymongo
import numpy as np 
import pandas as pd 
import datetime as dt
import random
import ruptures as rpt
#from cryptoApp.mongoService.setup import getMongoClient
#from cryptoApp.mongoService.queries import queryDatabase


def query_database(coin):
    """ queries the crypto database for price and volume 
    :param coin: String, coin ticker as used in cryptoscraper
    :return: database cursor of specific coin sorted by timestamp
    """

    #client = configure_db()
    client = getMongoClient()
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
    unix_time = []

    for entry in cursor:
        volume.append(entry['volumefrom'])
        price.append(entry['high'])
        unix_time.append(int(entry['time']))
        #timestamp_string.append(dt.datetime.fromtimestamp(int(entry['time'])).strftime('%d.%m.%Y %H:%M:%S'))
        t = dt.datetime.fromtimestamp(int(entry['time']))
        timestamp.append(np.datetime64(t))

    timeseries = pd.DataFrame(data = {'volume' : volume , 'price' : price, 'time' : timestamp, 'unix_time' : unix_time }, index=timestamp)

    return timeseries

def get_change_point_dates(timeseries, label, from_date, to_date):
    signal = timeseries[label].loc[from_date:to_date].values
    timeline = timeseries.loc[from_date:to_date].index

    algo = rpt.Pelt(model="rbf").fit(signal)
    result = algo.predict(pen=10)

    return np.take(timeline, [x - 1 for x in result])    

def generate_whole_timeseries(coin):
    """ wrapper to generate time series for a specific coin
    :param coin: String, coin ticker
    :return: pandas DataFrame times series with columns price, volume and index of time
    """
    cursor = query_database(coin)
    timeseries = build_timeline(cursor)
    return timeseries



#t = generate_whole_timeseries('BTC')




