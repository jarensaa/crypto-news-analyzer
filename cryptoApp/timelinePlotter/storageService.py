from cryptoApp.mongoService.queries import queryDatabase
from cryptoApp.mongoService.setup import getMongoClient
from cryptoApp.mongoService.setup import validateMongoEnvironment
import json
from pprint import pprint


def buildTimeline(client, seriesId):
    query = {
        "seriesId": seriesId
    }
    collection = client.reddit_data.aggregation
    returnedData = queryDatabase(collection, query)

    for data in returnedData:
        data["_id"] = "null"

    with open('cryptoApp/timelinePlotter/static/timeline.json', 'w+') as outputFile:
        json.dump(returnedData, outputFile)


def buildSocialMediaEvents(client, seriesId):
    query = {
        "seriesId": seriesId
    }
    collection = client.reddit_data.timeline_events
    returnedData = queryDatabase(collection, query)

    for data in returnedData:
        data["_id"] = "null"

    with open('cryptoApp/timelinePlotter/static/media_events.json', 'w+') as outputFile:
        json.dump(returnedData, outputFile)


def buildSocialMediaSeries(seriesId):
    validateMongoEnvironment()
    client = getMongoClient()
    buildTimeline(client, seriesId)
    buildSocialMediaEvents(client, seriesId)
    client.close()


def buildCryptoDataSeries(fromTime, toTime, currency):
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
    for data in returnedData:
        data["_id"] = "null"

    with open('cryptoApp/timelinePlotter/static/crypto.json', 'w+') as outputFile:
        json.dump(returnedData, outputFile)

    client.close()
    return
