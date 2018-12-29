from cryptoApp.mongoService.setup import getMongoClient
from cryptoApp.mongoService.queries import queryDatabase
from cryptoApp.cryptoHandler.modelTimeline import get_change_point_dates
from cryptoApp.cryptoHandler.modelTimeline import generate_whole_timeseries
import pandas as pd

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
    
    for entry in range(len(timeseries['price'])):
        start = timeseries['time'].iloc[entry]
        end = timeseries['time'].iloc[win+entry]
        t = get_change_point_dates(timeseries, 'price', start, end)
    signal = timeseries['price']
    return timeseries

t = scan_for_change_points('BTC')
