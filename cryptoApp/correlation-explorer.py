from cryptoApp.mongoService.setup import validateMongoEnvironment, getMongoClient
from cryptoApp.mongoService.queries import queryDatabase
from cryptoApp.constants.unixTime import DAY
from cryptoApp.constants.unixTime import HOUR
from cryptoApp.constants.cryptoRegistry import BITCOIN
from cryptoApp.constants.cryptoRegistry import cryptocurrencies
from cryptoApp.timelinePlotter.storageService import buildCryptoChangepointEvents
from cryptoApp.timelinePlotter.storageService import buildSocialMediaSeries
from cryptoApp.timelinePlotter.storageService import buildCryptoDataSeries
from cryptoApp.socialMediaAggregator.aggregator import runAggregator
from cryptoApp.timelinePlotter.plotter import plot
from cryptoApp.socialMediaEventDetection.detector import runEventDetector
from numpy import correlate
from time import mktime
from datetime import datetime
from pprint import pprint
import sys
import bisect
import random


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


def hasValueInRange(numberArray, rangeStart, rangeEnd):
    i = bisect.bisect_right(numberArray, rangeEnd)
    if(i == 0):
        return False

    value = numberArray[i-1]
    if(value >= rangeStart):
        return True

    return False


def analyseEvents(changepoints, mediaEvents, backDelay, frameSize, roundDigits):

    mediaGivenChangepointCount = 0
    notMediaGivenChangepointCount = 0
    changepointGivenMediaCount = 0
    notChangepointGivenMediaCount = 0

    for changepoint in changepoints:
        if(hasValueInRange(mediaEvents, changepoint-backDelay-frameSize, changepoint-backDelay)):
            mediaGivenChangepointCount += 1
        else:
            notMediaGivenChangepointCount += 1

    for mediaEvent in mediaEvents:
        if(hasValueInRange(changepoints, mediaEvent+backDelay, mediaEvent+backDelay+frameSize)):
            changepointGivenMediaCount += 1
        else:
            notChangepointGivenMediaCount += 1

    result = [mediaGivenChangepointCount/len(changepoints), notMediaGivenChangepointCount/len(changepoints),
              changepointGivenMediaCount/len(mediaEvents), notChangepointGivenMediaCount/len(mediaEvents)]

    return [round(x, roundDigits) for x in result]


def analyseRandomData(changepoints, mediaEvents, trails, backDelay, frameSize, roundDigits):

    randomMediaSum = [0, 0, 0, 0]
    randomChangeSum = [0, 0, 0, 0]
    randomAllSum = [0, 0, 0, 0]

    for i in range(trails):
        randomChangepoints = getRandomNumbers(len(changepoints), startTime, endTime)
        randomMediaEvents = getRandomNumbers(len(mediaEvents), startTime, endTime)

        randomMediaResult = analyseEvents(changepoints, randomMediaEvents, backDelay, frameSize, roundDigits)
        randomChangeResult = analyseEvents(randomChangepoints, mediaEvents, backDelay, frameSize, roundDigits)
        randomAllResults = analyseEvents(randomChangepoints, randomMediaEvents, backDelay, frameSize, roundDigits)

        randomMediaSum = [sum(pair) for pair in zip(randomMediaSum, randomMediaResult)]
        randomChangeSum = [sum(pair) for pair in zip(randomChangeResult, randomChangeSum)]
        randomAllSum = [sum(pair) for pair in zip(randomAllResults, randomAllSum)]

    randomMediaSum = [round(x/trails, roundDigits) for x in randomMediaSum]
    randomChangeSum = [round(x/trails, roundDigits) for x in randomChangeSum]
    randomAllSum = [round(x/trails, roundDigits) for x in randomAllSum]

    return [randomMediaSum, randomChangeSum, randomAllSum]


def getRandomNumbers(number, minTime, maxTime):
    numbers = []
    for i in range(number):
        numbers.append(random.randint(minTime, maxTime))
    return sorted(numbers)


days = 70
startTime = int(mktime(datetime(2017, 9, 1, 0, 00, 00).timetuple()))
endTime = startTime + days * DAY
currency = BITCOIN
tag = cryptocurrencies[currency]["tag"]

peakDetectionWindowSize = 10
peakDetectionSensitivity = 1.5

frameSize = 2*HOUR
backDelay = 0*HOUR

roundDigits = 5

randomTrails = 1000

validateMongoEnvironment()
client = getMongoClient()

series = getSeriesId(client, startTime, endTime)


if("--plot" in sys.argv):
    if(series == None):
        seriesId = runAggregator(startTime, endTime, tag, submissionScoreWeight=1,
                                 submissionWeight=10, commentWeight=5, commentScoreWeight=0.5)
    else:
        seriesId = series["_id"]
    buildCryptoChangepointEvents(startTime, endTime, currency)
    runEventDetector(seriesId, peakDetectionWindowSize, peakDetectionSensitivity)
    buildSocialMediaSeries(seriesId)
    buildCryptoDataSeries(startTime, endTime, currency)
    plot()
else:
    if(series == None):
        client.close()
        print("No social media timeseries fond for start and end-time combination")
        exit()
    castChangepointValuesToNumbers(client)
    mediaEvents = sorted([x["time"] for x in getMediaEvents(client, series["_id"])])
    changepoints = sorted(list(set([x["changepoint"] for x in getChangepoints(client, startTime, endTime, currency)])))
    print("p(media|change)  , p(change|media) ")
    print("{} <- Results on actual data".format(analyseEvents(changepoints, mediaEvents, backDelay, frameSize, roundDigits)))
    randomResults = analyseRandomData(changepoints, mediaEvents, randomTrails, backDelay, frameSize, roundDigits)
    print("{} <- Random values for media events. {} trails".format(randomResults[0], randomTrails))
    print("{} <- Random values for changepoints. {} trails".format(randomResults[1], randomTrails))
    print("{} <- Random values for media events and changepoints. {} trails".format(randomResults[2], randomTrails))

client.close()
