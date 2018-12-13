import praw
import os

REDDIT_URL_PREFIX = "https://www.reddit.com"

REDDIT_CLIENT_ID = os.environ.get('REDDIT_CLIENT_ID')
REDDIT_CLIENT_SECRET = os.environ.get('REDDIT_CLIENT_SECRET')
REDDIT_USER_AGENT = "linux:Scraper:0.1 (by /u/knowwebknowweb)"


def getSubmission(permalink, reddit):
    """ Get a submission based on a reddit permalink

    Arguments:
      permalink {string} -- A permalink to a post on the form "/r/<subreddit>/path/to/submission"
      reddit {praw.reddit} -- A reddit instance generated by praw.

    Returns:
      praw.submission -- A praw pointer to the post
    """

    submissionUrl = REDDIT_URL_PREFIX + permalink
    submission = reddit.submission(url=submissionUrl)
    return submission


def getSubmissionScore(submission):
    """ Gets the score on a given submission

    Arguments:
      submission {praw.submission} -- A praw pointer to a reddit submission

    Returns:
      int -- Score on the post
    """
    return submission.score


def getSubmissionComments(submission, tag):
    submissionPermalink = submission.permalink
    submissionComments = submission.comments
    submissionComments.replace_more(limit=20)

    comments = []
    for comment in submissionComments.list():
        comment = {
            "timestamp": comment.created_utc,
            "submission_permalink": submissionPermalink,
            "permalink": comment.permalink,
            "score": comment.score,
            "tag": tag
        }
        comments.append(comment)

    return comments


def getRedditInstance():
    """ Generates a new reddit instance based on the set environment variables

    Returns:
      praw.reddit -- A new reddit instance
    """

    return praw.Reddit(client_id=REDDIT_CLIENT_ID,
                       client_secret=REDDIT_CLIENT_SECRET,
                       user_agent=REDDIT_USER_AGENT)


def validateRedditEnvironment():
    """ Validates if all required environment variables are set.

    Returns:
      boolean -- True if environment is valid, False if not.
    """

    env_variables = ['REDDIT_CLIENT_ID', 'REDDIT_CLIENT_SECRET']
    missingEnvVariable = False

    for variable in env_variables:
        variableValue = os.environ.get(variable)
        if (variableValue == None):
            print("Missing env variable: " + variable)
            missingEnvVariable = True

    return not missingEnvVariable