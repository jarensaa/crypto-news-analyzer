
import pandas as pd
import time
import datetime as dt
import numpy as np
import json
import requests
import pymongo
import os 
from ratelimit import limits, sleep_and_retry
from tqdm import tqdm

SECOND = 1

@sleep_and_retry
@limits(calls=20, period=SECOND)
def call_api(url):
    response = requests.get(url)

    if response.status_code != 200:
        raise Exception('API response: {}'.format(response.status_code))
    return response


def configure_db():
    """ configure local mongodb instance 
    :return: collection to store data in 
    # TODO: structure mongodb collection and configuration
    # TODO: set environment variables in server
    """

    try: 
        # adjust this in local and server environment
        pw = os.environ.get('MONGOPW')
        name = os.environ.get('MONGOUSER')
        client = pymongo.MongoClient("mongodb+srv://{}:{}@cluster-kaw-loi4k.mongodb.net/test?retryWrites=true"\
            .format(pw,name))
        print("Connected successfully.") 
    
    except:   
        print("Could not connect to MongoDB") 
    
    
    return client


def store_data(data, client, callnum, coin):
    """ store data in mongodb collection
    :param data: json data object containing the data to be stored
    :param collection: mongodb collection to store into
    :param callnum: int, current number of call for progressbar
    :param coin: String, Coin ticker as used in scrape_data()
    """

    db = client.cryptoposts
    collection = db.cryptodata

    print("Inserting data into "+ str(collection.name)+ ", week " + str(callnum))

    for entry in tqdm(data):
        entry["coin"]=coin
        collection.insert_one(entry)
     

def scrape_data(coins, ts_from, ts_to, granularity="histohour?"):
    """
    scrape data and store it in MongoDB
    :param coins: Array of Strings including the ticker, e.g. ["BTC","ETH"]
    :param ts_from: start time string in the following format "DD.MM.YYYY"
    :param ts_to: start time string in the following format "DD.MM.YYYY"
    :param granularity: string defining which api granularity to call
    """

    client = configure_db()
    timestamps = parse_time_frame(ts_from,ts_to)

    
    for coin in coins:
        for i in range(len(timestamps)):
            url = 'https://min-api.cryptocompare.com/data/{}fsym={}&tsym=USD&toTs={}'\
                .format(granularity, coin, str(timestamps[i]))

            page = call_api(url)
            data = page.json()['Data']
            store_data(data, client, i, coin)

    client.close()


def parse_time_frame(ts_from, ts_to, timeformat="%d.%m.%Y"):
    """ computes the unix timestamps to cover the entire time frame 
    :param ts_from: string, starting date (chronological) in format "DD.MM.YYYY" 
    :param ts_to: string, ending date in format "DD.MM.YYYY"
    :return: array of unix timestamps to be passed to api call
    """

    ts_to =  dt.datetime.strptime(ts_to, timeformat)
    ts_from =  dt.datetime.strptime(ts_from, timeformat)
    time_period =  ts_to - ts_from

    if time_period.days < 0: 
        raise ValueError('Time Frame is {} days'.format(str(time_period.days)))
    
    timestamps = []
    ts_current = ts_from
    num_calls = int(np.ceil(time_period.days/7)) 

    for _ in range(num_calls): 

        ts_unix = time.mktime(ts_current.timetuple())
        timestamps.append(ts_unix)
        ts_current += dt.timedelta(7) 

    return timestamps

# show example call 
#scrape_data(['BTC','ETH'],"9.12.2016","8.12.2017")
