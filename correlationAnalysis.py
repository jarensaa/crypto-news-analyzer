from cryptoApp.cryptoHandler.modelTimeline import generate_whole_timeseries
from cryptoApp.mongoService.setup import getMongoClient
from cryptoApp.mongoService.queries import queryDatabase
from cryptoApp.mongoService.setup import validateMongoEnvironment
from correlationService import generate_social_timeseries
from correlationService import generate_crypto_timeseries
from correlationService import correlate_timeseries
import pandas as pd
import numpy as np
from random import randint

def compute_correlation(currency, ticker, dbgran = 24, stride = 3, fromTime=1504216800, toTime=1512853200):  
    """


    """

    stride = stride * 24
    validateMongoEnvironment()
    client = getMongoClient()
    collection = client.cryptoposts.changepoints
    query = {
        "changepoint": {
            "$gte": fromTime,
            "$lt": toTime
        }
    }
    changepoints = queryDatabase(collection, query)
    #df = pd.DataFrame(changepoints)
    #df['datetime'] = pd.to_datetime(df['changepoint'], unit='s')

    correlations = []
    for changepoint in changepoints:
        #print(df['datetime'].iloc[i])
        social = generate_social_timeseries(changepoint['start'], changepoint['end'], currency, sid='4ffa1742-1034-11e9-bcd3-c49ded20dae1')
        crypto = generate_crypto_timeseries(changepoint['start'], changepoint['end'], ticker)
        rand = randint(0,len(changepoints)-1)
        print(rand)
        socialRandom = generate_social_timeseries(changepoints[rand]['start'], changepoints[rand]['end'], currency, sid='4ffa1742-1034-11e9-bcd3-c49ded20dae1')
        price, social, x, lags, ccor = correlate_timeseries(crypto, social)
        price, social, x, lags, ccorR = correlate_timeseries(crypto, socialRandom)
        maxcorr = max(ccor)
        maxcorrR = max(ccorR)
        maxlag = lags[np.argmax(ccor)]
        data = {}
        data["corr"] = maxcorr
        data["corrR"] = maxcorrR
        data["maxlag"] = maxlag
        data["changepoint"] = changepoint
        correlations.append(data)
        print("max correlation is at lag %d" % maxlag)

    return correlations


#corr = compute_correlation('bitcoin', 'BTC') 
#corr = pd.DataFrame(corr)
corr = pd.read_pickle('corr.pkl')

print("H")
