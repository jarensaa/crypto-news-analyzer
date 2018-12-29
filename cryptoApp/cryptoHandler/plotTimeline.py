import matplotlib.pyplot as plt
import numpy as np 
import pandas as pd 
import datetime as dt
import random
import ruptures as rpt
from cryptoApp.cryptoHandler.modelTimeline import generate_whole_timeseries

def plot_price_volume(from_date, to_date, timeseries):
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

def plot_change_points(timeseries, label, from_date, to_date):
    signal = timeseries[label].loc[from_date:to_date].values
    timeline = timeseries.loc[from_date:to_date].index

    algo = rpt.Pelt(model="rbf").fit(signal)
    result = algo.predict(pen=10)

    plt.plot(timeline, signal, 'b-')
    for xc in np.take(timeline, [x - 1 for x in result]):
        plt.axvline(x=xc, color='black', linestyle='--')

    plt.show()




# example plot of price and volume for given timespan
#plot_price_volume("20161202", "20161210", timeseries)
# example plot of change points using PELT
#plot_change_points(timeseries, 'price', "20161202", "20161210")
# example of retrieving change point dates
#cp_dates = get_change_point_dates(timeseries, 'price', "20161202", "20161210")
