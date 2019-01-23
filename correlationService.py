import pandas as pd 
import datetime as dt
import numpy as np
from scipy import signal
#from correlationPlotter import plot_correlation
from cryptoApp.socialMediaAggregator.aggregator import runAggregator
from cryptoApp.mongoService.queries import queryDatabase
from cryptoApp.mongoService.setup import getMongoClient
from cryptoApp.mongoService.setup import validateMongoEnvironment




def generate_social_timeseries(fromTime, toTime, coin, sid=None):
    """ generates an aggregated social media time series within 
        a time frame for a specific coin
    :param start: unix timestamp, starting point
    :param end: unix timestamp, ending point
    :param coin: coin string, eg. 'bitcoin'

    """
    if not sid:
        sid = runAggregator(fromTime, toTime,coin)
    
    # example series id 
    # s_id = '2e0859d0-0b81-11e9-b0f7-a0d37ae9eda5'

    validateMongoEnvironment()
    client = getMongoClient()
    query = {
        "seriesId": sid,
        "startTime": {
            "$gte": fromTime,
            "$lt": toTime
        }
        
    }

    collection = client.reddit_data.aggregation
    returnedData = queryDatabase(collection, query)
    df = pd.DataFrame(returnedData)
    client.close()

    return df

def generate_crypto_timeseries(fromTime, toTime, currency):
    """ generates a crypto time series within a time frame 
        for a specific coin
    :param start: unix timestamp, starting point
    :param end: unix timestamp, ending point
    :param coin: coin string, eg. 'bitcoin'
    :return: pd DataFrame of the queried results
    """

    validateMongoEnvironment()
    client = getMongoClient()
    collection = client.cryptoposts.crypto

    query = {
        "coin": currency,
        "time": {
            "$gte": fromTime,
            "$lt": toTime
        }
    }

    returnedData = queryDatabase(collection, query)
    df = pd.DataFrame(returnedData)
    client.close()

    return df

def auto_correlate(x):
    x = x['sum']
    nx = len(x) 
    x = np.random.randn(nx) # normal RV

    lags = np.arange(-nx + 1, nx) # so last value is nx - 1

    # Remove sample mean
    xdm = x - x.mean()

    autocorr_xdm = np.correlate(xdm, xdm, mode='full')
    
    # Normalize by the zero-lag value:
    autocorr_xdm /= autocorr_xdm[nx - 1]
    return autocorr_xdm, lags 

    

def correlate_timeseries(crypto_timeseries, social_timeseries):
    crypto_timeseries['date'] = pd.to_datetime(crypto_timeseries['time'],dayfirst=True, unit='s')
    price = crypto_timeseries['high']
    social = social_timeseries['sum']

    # drop additional price data hour 
    price = price.drop(price.index[len(price)-1])

    n = len(price)
    x = crypto_timeseries['date'][0:len(price)]

    lags = np.arange(-n + 1, n)
    ccov = np.correlate(price - price.mean(), social - social.mean(), mode='full')
    ccor = ccov / (n * social.std() * social.std())

    return price, social, x, lags, ccor


def compute_correlation_of_segments():
    crypto1 = generate_crypto_timeseries(1517529600, 1518220800, 'BTC')
    social = generate_social_timeseries(1512172800, 1512864000, 'bitcoin')
    price, social, x, lags, ccor = correlate_timeseries(crypto1, social)
    #plot_correlation(price, social, x, lags, ccor)

    # to compare against other random time series 
    #crypto2 = generate_crypto_timeseries(1512172800, 1512864000, 'BTC')
    #cor2 = correlate_timeseries(crypto2, social)


if __name__ == "__main__":
    compute_correlation_of_segments()
