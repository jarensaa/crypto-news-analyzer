
import pandas as pd
import time
import datetime as dt
import numpy as np
import json
import requests
import pymongo


def configure_local_db():
    """ configure local mongodb instance 
    :return: collection to store data in 
    # TODO: structure mongodb collection and configuration
    """

    try: 
        client = pymongo.MongoClient() 
        print("Connected successfully.") 
    except:   
        print("Could not connect to MongoDB") 
    
    db = client.cryptoposts
    collection = db.cryptocompare
    return collection


def store_data(data, collection):
    """ store data in mongodb collection
    :param data: json data object containing the data to be stored
    :param collection: mongodb collection to store into
    """
    for entry in data:
        collection.insert_one(entry)
     

def scrape_data(coins, ts_from, ts_to, granularity="histohour?"):
    """
    scrape data and store it in mongodb
    :param coins: Array of Strings including the ticker, e.g. ["BTC","ETH"]
    :param ts_from: start time string in the following format "DD.MM.YYYY"
    :param ts_to: start time string in the following format "DD.MM.YYYY"
    :param granularity: string defining which api granularity to call
    """

    # TODO: change granularity by changing api string to query 
    collection = configure_local_db()
    timestamps = parse_time_frame(ts_from,ts_to)

    
    for coin in coins:
        for ts_call in timestamps:
            url = 'https://min-api.cryptocompare.com/data/{}fsym={}&tsym=USD&toTs={}'\
                .format(granularity, coin, str(ts_call))

            page = requests.get(url)
            data = page.json()['Data']
            store_data(data, collection)



def parse_time_frame(ts_from, ts_to, timeformat="%d.%m.%Y"):
    """ computes the unix timestamps to cover the entire time frame 
    :param ts_from: string, starting date (chronological) in format "DD.MM.YYYY" 
    :param ts_to: string, ending date in format "DD.MM.YYYY"
    :return: array of unix timestamps to be passed to api call
    """
    # TODO: timeformat in general settings
    # TODO: consider timestamp conversion for different timezone

    ts_to =  dt.datetime.strptime(ts_to, timeformat)
    ts_from =  dt.datetime.strptime(ts_from, timeformat)
    time_period =  ts_to - ts_from

    timestamps = []
    ts_current = ts_from
    num_calls = int(np.ceil(time_period.days/7)) 

    for _ in range(num_calls): 

        ts_unix = time.mktime(ts_current.timetuple())
        timestamps.append(ts_unix)
        ts_current += dt.timedelta(7) 

    return timestamps

# show example call 
scrape_data(['BTC'],"1.04.2018","13.10.2018")
