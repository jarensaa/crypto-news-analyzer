from cryptoApp.mongoService.setup import getMongoClient, validateMongoEnvironment
from cryptoApp.mongoService.queries import queryDatabase
from cryptoApp.mongoService.queries import bulkPostToDatabase
import math


def getTimeline(timelineId, client):
    collection = client.reddit_data.aggregation
    query = {
        "seriesId": timelineId
    }

    return queryDatabase(collection, query)


def findEvents(aggregatedData):
    minTime = math.inf
    maxTime = 0
    for dataPoint in aggregatedData:
        minTime = min(minTime, dataPoint["startTime"])
        maxTime = max(maxTime, dataPoint["endTime"])

    middle = int((minTime + maxTime) / 2)
    lastQuarter = int((middle+maxTime)/2)
    return [middle, lastQuarter]


def postEventsToDatabase(client, timelineId, events):
    collection = client.reddit_data.timeline_events
    objects = []
    for event in events:
        objects.append({
            "seriesId": timelineId,
            "time": event
        })
    bulkPostToDatabase(collection, objects)


def runEventDetector(timelineId):
    validateMongoEnvironment()
    client = getMongoClient()
    timeline = getTimeline(timelineId, client)
    events = findEvents(timeline)
    postEventsToDatabase(client, timelineId, events)
    client.close()


timelineId = "4522b66a-0b86-11e9-ad04-c49ded20dae1"
runEventDetector(timelineId)
