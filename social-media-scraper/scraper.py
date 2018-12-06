from queryPushshiftApi import queryPushshift
from pprint import pprint
from queryRedditApi import getSubmission, validateRedditEnvironment, getSubmissionScore, getRedditInstance
from mongoDbEngine import validateMongoEnvironment, getMongoClient
from datetime import datetime
import time

StartTime = datetime.now()


def validateEnvironments():
    if(not validateRedditEnvironment()):
        quit()

    if(not validateMongoEnvironment()):
        quit()


def getSubmissionsFromPushshift():
    retryLimit = 5
    retryCounter = 0

    while(retryCounter < retryLimit):

        (cleanedSubmissions, timeFrom, timeTo) = queryPushshift(
            1544004364, 1544090764, "cryptocurrency", 10, 40)

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


def addRedditDataToSubmissions(submissions):
    # The reddit instance offers built-in rate limit checks. We therefore use the same instance for all calls.
    reddit_instance = getRedditInstance()

    StartTime = datetime.now()
    for index, post in enumerate(submissions):
        if(index % 5 == 0):
            print("{:3d} out of {:3d} posts fetched from reddit. Used {:3d}seconds".format(
                index, len(submissions), (datetime.now() - StartTime).seconds))
            StartTime = datetime.now()
        permalink = post['permalink']
        reddit_submission_instance = getSubmission(permalink, reddit_instance)
        post['score'] = getSubmissionScore(reddit_submission_instance)


def storeSubmissionsInMongoDB(submissions):
    mongoClient = getMongoClient()
    collection = mongoClient.reddit_data.submissions
    collection.insert_many(submissions)
    mongoClient.close()


validateEnvironments()
submissions = getSubmissionsFromPushshift()
addRedditDataToSubmissions(submissions)
storeSubmissionsInMongoDB(submissions)
