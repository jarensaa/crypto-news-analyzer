from cryptoApp.mongoService.setup import getMongoClient
from cryptoApp.mongoService.queries import queryDatabase
from cryptoApp.cryptoHandler.modelTimeline import get_change_point_dates
from cryptoApp.cryptoHandler.modelTimeline import generate_whole_timeseries
import pandas as pd
import numpy as np

def scan_for_change_points(coin, granularity=7, stride=3, dbgran=24):
    """ scans entire available time series of coin for change points 
        applying a sliding window
        :param fromTime: coin ticker, eg 'BTC'
        :param granularity: size of sliding window in days
        :param stride: size of stride in days
        :param dbgran: database granularity used to store values in mongodb
            default is hours, multiply by 24
    """
    timeseries = generate_whole_timeseries(coin)

    win = granularity * dbgran
    stride = stride * 24
    
    for entry in range(0,len(timeseries['price']),stride):
        start = timeseries['time'].iloc[entry]
        end = timeseries['time'].iloc[win+entry]
        changepoints = get_change_point_dates(timeseries, 'price', start, end)

        start_unix = timeseries['unix_time'].iloc[entry]
        end_unix = timeseries['unix_time'].iloc[win+entry]
        store_changepoint(changepoints, start_unix, end_unix, coin)


    return timeseries


def store_changepoint(cpoints, start, end, coin):
    """ stores detected changepointss
    :param changepoint: 
    :param start: string of startdate, YYYYMMDD
    :param end: string of enddate, YYYYMMD
    :param coin: coin string, eg. 'BTC'
    """
    
    client = getMongoClient()
    collection = client.cryptoposts.changepoints

    entries = []
    for date in cpoints:
        entry = {}
        unix = int(date.value/10**9)
        entry["changepoint"] = str(unix)
        entry["start"] = str(start)
        entry["end"] = str(end)
        entry["coin"] = str(coin)
        entries.append(entry)
    
    valid = collection.insert_many(entries)

    client.close()

t = scan_for_change_points('BTC')
