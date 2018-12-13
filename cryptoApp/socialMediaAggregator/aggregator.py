from cryptoApp.mongoService.setup import validateMongoEnvironment
from cryptoApp.mongoService.setup import getMongoClient
from cryptoApp.mongoService.queries import queryDatabase
from cryptoApp.mongoService.queries import bulkPostToDatabase
from cryptoApp.constants.unixTime import HOUR, DAY
from pprint import pprint
from time import mktime
from datetime import datetime
import uuid


def buildQuery(startTime, endTime, tag):
    """Builds a range query based on time and a tag

    Arguments:
      startTime {float} -- Unix time, start of range to query.
      endTime {float} -- Unix time, end of range to query.
      tag {string} -- The tag of the data. E.g 'bitcoin'

    Returns:
      string -- A mongoDb compatible query.
    """

    return {
        "timestamp": {
            "$gte": startTime,
            "$lt": endTime
        },
        "tag": tag
    }


def getCommentAggregation(comments, commentWeight):
    return len(comments) * commentWeight


def getCommentScoreAggregation(comments, commentScoreWeight):
    score = 0
    for comment in comments:
        score += int(comment["score"])
    return score


def getSubmissionAggregation(submissions, submissionWeight):
    return len(submissions)*submissionWeight


def getSubmissionScoreAggregation(submissions, submissionScoreWeight):
    score = 0
    for submission in submissions:
        score += int(submission["score"])
    return score


def getAggregation(mongoClient, startTime, endTime, tag, granularity=HOUR, submissionWeight=3, submissionScoreWeight=1, commentWeight=2, commentScoreWeight=1):
    """ Gets data from mongoDB and aggregates it based on the provided weights and granularity.

    Arguments:
      mongoClient {pymongo.client} -- A mongoDB client to use for querying
      startTime {float} -- Unix time, start of range to query.
      endTime {float} -- Unix time, end of range to query.
      tag {string} -- The tag of the data. E.g 'bitcoin'

    Keyword Arguments:
      granularity {int} -- The step size in the time dimension to aggregate on (default: {HOUR})
      submissionWeight {int} -- The weight given to the existence of a submission (default: {3})
      submissionScoreWeight {int} -- The weight given to the score of a submission (default: {1})
      commentWeight {int} -- The weight given to the existence of a comment (default: {2})
      commentScoreWeight {int} -- The weight given to the score of a comment (default: {1})

    Returns:
      (string, list)
      string -- The generated uuid used to tag the timeline, corresponding to the seriesId in mongoDB
      list -- The produced aggregated data
    """

    aggregations = []
    aggregationId = str(uuid.uuid1())

    while(startTime < endTime):
        queryFromTime = startTime
        queryToTime = startTime + granularity

        submissionQuery = buildQuery(queryFromTime, queryToTime, tag)
        commentQuery = buildQuery(queryFromTime, queryToTime, tag)

        submissions = queryDatabase(mongoClient.reddit_data.submissions, submissionQuery)
        comments = queryDatabase(mongoClient.reddit_data.comments, commentQuery)

        commentAggregation = getCommentAggregation(comments, commentWeight)
        commentScoreAggregation = getCommentScoreAggregation(comments, commentScoreWeight)
        submissionAggregation = getSubmissionAggregation(submissions, submissionWeight)
        submissionScoreAggregation = getSubmissionScoreAggregation(submissions, submissionScoreWeight)
        weightedSum = commentAggregation + commentScoreAggregation + submissionAggregation + submissionScoreAggregation

        aggregation = {
            "startTime": queryFromTime,
            "endTime": queryToTime,
            "timeGranularity": granularity,
            "tag": tag,
            "seriesId": aggregationId,
            "comments": commentAggregation,
            "commentScores": commentScoreAggregation,
            "submissions": submissionAggregation,
            "submissionScores": submissionScoreAggregation,
            "sum": weightedSum
        }

        aggregations.append(aggregation)
        startTime = queryToTime

    return aggregationId, aggregations


def runAggregator(startTime, endTime, tag, granularity=HOUR, submissionWeight=3, submissionScoreWeight=1, commentWeight=2, commentScoreWeight=1):
    """ Gets data from mongoDB, aggregates it, and posts the results back to mongodb. Returns an unique identifier for the timeseries.
    The aggregation values are calculated based on the provided weights.

    Arguments:
      startTime {float} -- Unix time, start of range to query.
      endTime {float} -- Unix time, end of range to query.
      tag {string} -- The tag of the data. E.g 'bitcoin'

    Keyword Arguments:
      granularity {int} -- The step size in the time dimension to aggregate on (default: {HOUR})
      submissionWeight {int} -- The weight given to the existence of a submission (default: {3})
      submissionScoreWeight {int} -- The weight given to the score of a submission (default: {1})
      commentWeight {int} -- The weight given to the existence of a comment (default: {2})
      commentScoreWeight {int} -- The weight given to the score of a comment (default: {1})

    Returns:
      string -- uuid used to tag the timeseries. Corresponds to the seriesId field in mongoDB.
    """

    validateMongoEnvironment()
    client = getMongoClient()
    print("Aggregating data about {} in the time interval [{},{}]".format(tag, startTime, endTime))

    (aggregationId, aggregation) = getAggregation(client, startTime, endTime, tag, granularity=granularity, submissionWeight=submissionWeight,
                                                  submissionScoreWeight=submissionScoreWeight, commentWeight=commentWeight, commentScoreWeight=commentScoreWeight)
    aggregationCollection = client.reddit_data.aggregation
    bulkPostToDatabase(aggregationCollection, aggregation)

    client.close()
    return aggregationId


def main():
    # YYYY MM DD HH MM SS
    startTime = mktime(datetime(2018, 12, 5, 12, 00, 00).timetuple())
    endTime = startTime + DAY
    tag = "bitcoin"
    createdId = runAggregator(startTime, endTime, tag)
    print("Created time series based on aggregation with id: ", createdId)


if __name__ == "__main__":
    main()
