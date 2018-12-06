from queryPushshiftApi import queryPushshift
from pprint import pprint
from queryRedditApi import getSubmission, validateRedditEnvironment, getSubmissionScore, getRedditInstance, getSubmissionComments
from mongoDbEngine import validateMongoEnvironment, getMongoClient
from datetime import datetime
from cryptoRegistry import BITCOIN, ETHEREUM, generateCoinScrapingData
import time


StartTime = datetime.now()


def validateEnvironments():
    """Check if all environment variables for reddit and mongodb is set. 
      The program terminates if this is not the case
    """

    if(not validateRedditEnvironment()):
        quit()

    if(not validateMongoEnvironment()):
        quit()


def getSubmissionsFromPushshift(fromTime, toTime, subreddit, keywords, root=True):
    """ Get submissions from the pushshift API by recursion. If the limit of the pushshift api is hit, the time slot is divided
    into two. The function is then called recursivly for each range.

    Arguments:
      fromTime {long} -- Unix timestamp indicating start of range to query over.
      toTime {long} -- Unix timestamp indicating end of range to query over.
      subreddit {string} -- Subreddit to query
      keywords {str} -- keywords used to search for posts within a subreddit

    Keyword Arguments:
      root {boolean} -- Indicates if the function is the root call.

    Returns:
      list() -- of submissions 
    """

    retryLimit = 5
    retryCounter = 0
    limit = 1000

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
    """ Queries the reddit api to append true scores to a post. Also fetches comments related to
        the posts.

    Arguments:
      submissions {list()} -- A list with submissions, ordered in prioritzed order for querying.
      tag {string} -- A tag relating the post to the query

    Keyword Arguments:
      min_comments {int} -- The minimum amount of comments which need to be on a 
                            submission for a query to be performed (default: {10})
      max_submission_api_calls {int} -- Max amount of API calls to the reddit API (default: {50})

    Returns:
      list() -- A list of comments related to the queried submissions.
    """

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
runScraper(ETHEREUM, 1543622400, 1544097600)
