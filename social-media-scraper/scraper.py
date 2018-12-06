from queryPushshiftApi import queryPushshift
from pprint import pprint
from queryRedditApi import getSubmission, validateRedditEnvironment, getSubmissionScore, getRedditInstance, getSubmissionComments
from mongoDbEngine import validateMongoEnvironment, getMongoClient
from datetime import datetime
from cryptoRegistry import BITCOIN, ETHEREUM, generateCoinScrapingData
import time


StartTime = datetime.now()


def validateEnvironments():
    if(not validateRedditEnvironment()):
        quit()

    if(not validateMongoEnvironment()):
        quit()


def getSubmissionsFromPushshift(fromTime, toTime, subreddit, keywords):
    retryLimit = 5
    retryCounter = 0

    print("Querying subreddit: {} for keywords {} in time interval [{:10d},{:10d}]".format(
        subreddit, keywords, fromTime, toTime))
    while(retryCounter < retryLimit):
        (cleanedSubmissions, timeFrom, timeTo) = queryPushshift(
            fromTime, toTime, subreddit, 10, 40, keywords=keywords)

        if(len(cleanedSubmissions) == 0):
            print("Failed to fetch posts from pushshift. Retrying...")
            retryCounter += 1
            time.sleep(10)
        else:
            break

    if(retryCounter == retryLimit):
        print("Can not connect to pushshift server.")
        quit()

    print("{:3d} submissions fetched from pushshift. Time used:{:3d}seconds".format(
        len(cleanedSubmissions), (datetime.now() - StartTime).seconds))

    return cleanedSubmissions


def addRedditDataToSubmissions(submissions, tag):
    # The reddit instance offers built-in rate limit checks. We therefore use the same instance for all calls.
    reddit_instance = getRedditInstance()
    comments = []

    StartTime = datetime.now()
    for index, post in enumerate(submissions):
        if(index % 5 == 0):
            print("{:3d} out of {:3d} posts fetched from reddit. Used {:3d}seconds".format(
                index, len(submissions), (datetime.now() - StartTime).seconds))
            StartTime = datetime.now()
        permalink = post['permalink']
        reddit_submission_instance = getSubmission(permalink, reddit_instance)
        post['score'] = getSubmissionScore(reddit_submission_instance)
        post["tag"] = tag
        comments += getSubmissionComments(reddit_submission_instance, tag)

    return comments


def storeSubmissionsInMongoDB(submissions):
    mongoClient = getMongoClient()
    collection = mongoClient.reddit_data.submissions
    collection.insert_many(submissions)
    mongoClient.close()


def storeCommentsInMongoDB(comments):
    mongoClient = getMongoClient()
    collection = mongoClient.reddit_data.comments
    collection.insert_many(comments)
    mongoClient.close()


validateEnvironments()
scrapingInput = generateCoinScrapingData(BITCOIN, 1544004364, 1544090764)

fromTime = scrapingInput["fromTime"]
toTime = scrapingInput["toTime"]
tag = scrapingInput["tag"]
subreddits = scrapingInput["subreddits"]

for subreddit in subreddits:
    subredditName = subreddit["subreddit"]
    keywords = subreddit["keywords"]
    submissions = getSubmissionsFromPushshift(fromTime, toTime, subredditName, keywords)
    comments = addRedditDataToSubmissions(submissions, tag)
    storeSubmissionsInMongoDB(submissions)
    storeCommentsInMongoDB(comments)
