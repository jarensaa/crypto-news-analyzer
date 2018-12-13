import time
import requests
from ratelimit import limits, sleep_and_retry

baseUrl = "https://api.pushshift.io/reddit/search/submission/"
MINUTE = 60


def buildQuery(timeFrom, timeTo, subreddit, size="100", keywords="", author="", aggs="", metadata="true", frequency="hour", advanced="false", sort="desc", domain="", sort_type="num_comments"):
    """Builds a url which can be used to query the pushshift API.

    Arguments:
      timeFrom {long} -- Unix time stamp indicating start of timerange to query
      timeTo {long} -- Unix time stamp indicating end of timerange to query
      subreddit {string} -- Subreddit to query

    Keyword Arguments:
      size {str} -- Amount of submissions to fetch within the timerange (default: {"1000"})
      keywords {str} -- keywords used to search for posts within a subreddit (default: {""})
      aggs {str} -- set aggrigations to be used by the pushshift api (default: {""})
      metadata {str} -- Include metadata search information (default: {"true"})
      frequency {str} -- Set aggregation frequency (default: {"hour"})
      advanced {str} -- Set advanced mode  ¯\_(ツ)_/¯ (default: {"false"})
      sort {str} -- sort directon of the data returned from pushshift (default: {"desc"})
      domain {str} -- restrict the query to a specific domain of submission (default: {""})
      sort_type {str} -- set sort type of data from pushshift api (default: {"num_comments"})

    Returns:
      [str] -- url which can be used to query the pushshift API with the set parameters
    """

    arguments = []
    arguments.append("q=" + keywords.replace(",", "%2C"))
    arguments.append("after="+str(timeFrom))
    arguments.append("before="+str(timeTo))
    arguments.append("subreddit=" + str(subreddit))
    arguments.append("aggs="+aggs)
    arguments.append("metadata="+metadata)
    arguments.append("frequency="+frequency)
    arguments.append("advanced="+advanced)
    arguments.append("sort="+sort)
    arguments.append("domain="+domain)
    arguments.append("sort_type="+sort_type)
    arguments.append("size=" + size)

    return str(baseUrl) + "?" + "&".join(arguments)


def extractFeaturesFromData(inputdata):
    """ Takes raw data from the pushshift API and reduces it to specific features.

    Arguments:
      inputdata {dict} -- input json from the pushshift api, sorted my num_comments
      minComments {int} -- Sets the minimum number of comments which has to be present on a submission.
      maxSubmissions {int} -- Sets the maximum amount of sumbmissions to retrieve

    Returns:
      list -- A list of json objects with only relevant features
    """

    cleanedPosts = []
    timeFrom = time.time()
    timeTo = 0

    for index, redditPost in enumerate(inputdata):
        cleanedPost = {}
        timestamp = redditPost["created_utc"]

        timeFrom = min(timeFrom, timestamp)
        timeTo = max(timeTo, timestamp)

        cleanedPost["timestamp"] = timestamp
        cleanedPost["score"] = redditPost["score"]
        cleanedPost["num_comments"] = int(redditPost["num_comments"])
        cleanedPost["permalink"] = redditPost["permalink"]
        cleanedPost["subreddit"] = redditPost["subreddit"]

        cleanedPosts.append(cleanedPost)

    return cleanedPosts


@sleep_and_retry
@limits(calls=200, period=MINUTE)
def queryPushshift(fromTime, toTime, subreddit, keywords="", limit="100"):
    """Gets and filters data from the Pushshift API

    Arguments:
      fromTime {long} -- Unix time, start of timerange to query.
      toTime {long} -- Unix time, end of timerange to query.
      subreddit {string} -- subreddit to query

    Keyword Arguments:
      keywords {str} -- keywords used to search for posts within a subreddit (default: {""})

    Returns:
      dict -- A list of json objects with filtered features.
    """

    queryString = buildQuery(fromTime, toTime, subreddit, keywords=keywords, size=limit)
    response = requests.get(queryString)
    redditPostData = response.json()['data']
    return extractFeaturesFromData(redditPostData)
