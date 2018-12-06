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


def getSubmissionsFromPushshift(fromTime, toTime, subreddit, keywords, root=True):
    retryLimit = 5
    retryCounter = 0
    limit = 1000

    # TODO: Add functionaliy for handling the case where the number of submissions is over the pushshift limit.
    # Initial thought: Check if number of returned posts are at the limit, divide interval in two and repeat query recursivly.
    # This is actually a fun algorithm which i would love to present. /Jens

    if(root):
        print("Querying subreddit: {} for keywords {} in time interval [{:10d},{:10d}]".format(
            subreddit, keywords, fromTime, toTime))
    while(retryCounter < retryLimit):
        submissions = queryPushshift(fromTime, toTime, subreddit, keywords=keywords, limit=str(limit))

        if(len(submissions) == 0):
            print("Failed to fetch posts from pushshift. Retrying...")
            retryCounter += 1
            time.sleep(10)
        else:
            break

    if(retryCounter == retryLimit):
        print("Can not connect to pushshift server.")
        quit()

    if(len(submissions) == limit):
        timerange = toTime - fromTime
        halfTime = int(timerange / 2)
        submissions = getSubmissionsFromPushshift(fromTime, toTime - halfTime, subreddit, keywords, root=False) + \
            getSubmissionsFromPushshift(fromTime + halfTime + 1, toTime, subreddit, keywords, root=False)

    if(root):
        # Alernative: Sort on time and divide into ranges. Sort each of these on commments for querying on the reddit api
        submissions = sorted(submissions, key=lambda k: k["num_comments"], reverse=True)
        print("{:3d} submissions fetched from pushshift. Time used:{:3d}seconds".format(
            len(submissions), (datetime.now() - StartTime).seconds))

    return submissions


def addRedditDataToSubmissions(submissions, tag, min_comments=10, max_submission_api_calls=50):
    print("Fetching data from reddit. Doing up to {:d} queries".format(
        min(max_submission_api_calls, len(submissions))))

    # The reddit instance offers built-in rate limit checks. We therefore use the same instance for all calls.
    reddit_instance = getRedditInstance()
    comments = []

    StartTime = datetime.now()
    queries = 0
    printPointer = 0
    for post in submissions:

        if(queries % 5 == 0 and queries > printPointer):
            print("{:5d} posts fetched from reddit. Used {:d} seconds".format(
                queries, (datetime.now() - StartTime).seconds))
            StartTime = datetime.now()
            printPointer = queries

        if(queries <= max_submission_api_calls and post["num_comments"] >= min_comments):
            queries += 1
            permalink = post['permalink']
            reddit_submission_instance = getSubmission(permalink, reddit_instance)
            post['score'] = getSubmissionScore(reddit_submission_instance)
            comments += getSubmissionComments(reddit_submission_instance, tag)

        post["tag"] = tag

    return comments


def storeSubmissionsInMongoDB(submissions):
    mongoClient = getMongoClient()
    collection = mongoClient.reddit_data.submissions
    collection.insert_many(submissions)
    print("Posted {:d} new submissions to MongoDB".format(len(submissions)))
    mongoClient.close()


def storeCommentsInMongoDB(comments):
    mongoClient = getMongoClient()
    collection = mongoClient.reddit_data.comments
    collection.insert_many(comments)
    print("Posted {:d} new comments to MongoDB".format(len(comments)))
    mongoClient.close()


def runScraper(cryptocurrency, fromTime, toTime):
    validateEnvironments()
    scrapingInput = generateCoinScrapingData(cryptocurrency, fromTime, toTime)

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


runScraper(BITCOIN, 1544004364, 1544090764)
