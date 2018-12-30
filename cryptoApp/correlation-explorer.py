from cryptoApp.mongoService.setup import validateMongoEnvironment, getMongoClient
from cryptoApp.mongoService.queries import queryDatabase
from cryptoApp.constants.unixTime import DAY
from cryptoApp.constants.cryptoRegistry import BITCOIN
from cryptoApp.constants.cryptoRegistry import cryptocurrencies
from numpy import correlate
from time import mktime
from datetime import datetime


def getSeriesId(client, startTime, endTime):
    collection = client.reddit_data.aggregation_index
    query = {
        "startTime": startTime,
        "endTime": endTime
    }

    return collection.find_one(query)


def getMediaEvents(client, seriesId):
    collection = client.reddit_data.timeline_events
    query = {
        "seriesId": seriesId
    }

    return queryDatabase(collection, query)


def castChangepointValuesToNumbers(client):
    collection = client.cryptoposts.changepoints
    query = {
        "changepoint": {"$type": "string"}
    }

    changepoints = queryDatabase(collection, query)
    for changepoint in changepoints:
        changepoint["changepoint"] = int(changepoint["changepoint"])
        changepoint["end"] = int(changepoint["end"])
        changepoint["start"] = int(changepoint["start"])
        collection.update_one({'_id': changepoint["_id"]}, {"$set": changepoint}, upsert=False)


def getChangepoints(client, startTime, endTime, currency):
    collection = client.cryptoposts.changepoints
    query = {
        "coin": currency,
        "changepoint": {
            "$gte": startTime,
            "$lte": endTime
        }
    }

    return queryDatabase(collection, query)


days = 10
startTime = int(mktime(datetime(2017, 11, 1, 0, 00, 00).timetuple()))
endTime = startTime + days * DAY
currency = BITCOIN
tag = cryptocurrencies[currency]["tag"]

validateMongoEnvironment()
client = getMongoClient()

series = getSeriesId(client, startTime, endTime)
if(series == None):
    client.close()
    print("No social media timeseries fond for start and end-time combination")
    exit()

mediaEvents = [x["time"] for x in getMediaEvents(client, series["_id"])]
castChangepointValuesToNumbers(client)
changepoints = [x["changepoint"] for x in getChangepoints(client, startTime, endTime, currency)]

print(correlate(mediaEvents, changepoints))

client.close()
