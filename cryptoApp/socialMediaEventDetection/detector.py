from cryptoApp.mongoService.setup import getMongoClient, validateMongoEnvironment
from cryptoApp.mongoService.queries import queryDatabase
from cryptoApp.mongoService.queries import bulkPostToDatabase
from pprint import pprint
import math


def getTimeline(timelineId, client):
    collection = client.reddit_data.aggregation
    query = {
        "seriesId": timelineId
    }

    return queryDatabase(collection, query)


def getS1score(k, i, inputArray):
    if(i - k < 0):
        return None
    if(i + k >= len(inputArray)):
        return None

    x = inputArray[i]["sum"]
    leftMax = -math.inf
    rightMax = -math.inf

    for leftIndex in range(i-k, i):
        leftMax = max(leftMax, x - inputArray[leftIndex]["sum"])

    for rightIndex in range(i+1, i+k+1):
        rightMax = max(rightMax, x - inputArray[rightIndex]["sum"])

    return (leftMax + rightMax)/2


def getMeanAndStd(scoreData):
    meanSum = 0
    ssum = 0

    for score in scoreData:
        meanSum += score["score"]

    mean = meanSum / len(scoreData)
    for score in scoreData:
        ssum += math.pow(score["score"] - mean, 2)

    std = math.sqrt(ssum / (len(scoreData)-1))

    return (mean, std)


def findEvents(aggregatedData, k, sensitivity):
    aggregatedData = sorted(aggregatedData, key=lambda k: k["startTime"])
    scores = []
    events = []

    if(len(aggregatedData) <= 2*k):
        return []

    for i in range(len(aggregatedData)):
        score = getS1score(k, i, aggregatedData)
        if(score):
            scores.append({
                "score": score,
                "time": aggregatedData[i]["endTime"]
            })

    (mean, std) = getMeanAndStd(scores)

    prevscore = 0
    prevIndex = 0
    for i in range(len(scores)):
        score = scores[i]
        if((score["score"] - mean) > (sensitivity * std) and score["score"] > 0):
            if(i - prevIndex < k):
                print(prevscore)
                print(score)
                if(prevscore > score["score"]):
                    continue
                events = events[:-1]

            events.append(score["time"])
            prevscore = score["score"]
            prevIndex = i

    return events


def postEventsToDatabase(client, timelineId, events, windowSize, sensitivity):
    collection = client.reddit_data.timeline_events
    objects = []
    timelineMetadata = client.reddit_data.aggregation_index.find_one({"_id": timelineId})
    for event in events:
        objects.append({
            "seriesId": timelineId,
            "time": event,
            "windowSize": windowSize,
            "sensitivity": sensitivity,
            "tag": timelineMetadata["tag"]
        })
    bulkPostToDatabase(collection, objects)


def runEventDetector(timelineId, peakWindowSize, sensitivity):
    validateMongoEnvironment()
    client = getMongoClient()
    timeline = getTimeline(timelineId, client)
    events = findEvents(timeline, peakWindowSize, sensitivity)
    postEventsToDatabase(client, timelineId, events, peakWindowSize, sensitivity)
    client.close()
