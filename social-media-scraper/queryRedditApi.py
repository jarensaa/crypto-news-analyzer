import praw
import os

reddit_url_prefix = "https://www.reddit.com"

REDDIT_CLIENT_ID = os.environ.get('REDDIT_CLIENT_ID')
REDDIT_CLIENT_SECRET = os.environ.get('REDDIT_CLIENT_SECRET')
REDDIT_PASSWORD = os.environ.get('REDDIT_PASSWORD')
REDDIT_USERNAME = os.environ.get('REDDIT_USERNAME')
REDDIT_USER_AGENT = "linux:Scraper:0.1 (by /u/knowwebknowweb)"


def getSubmission(permalink, reddit):
    submissionUrl = reddit_url_prefix + permalink
    submission = reddit.submission(url=submissionUrl)
    return submission


def getSubmissionScore(submission):
    return submission.score


def getRedditInstance():
    return praw.Reddit(client_id=REDDIT_CLIENT_ID,
                       client_secret=REDDIT_CLIENT_SECRET,
                       user_agent=REDDIT_USER_AGENT)


def validateRedditEnvironment():
    env_variables = ['REDDIT_CLIENT_ID', 'REDDIT_CLIENT_SECRET',
                     'REDDIT_PASSWORD', 'REDDIT_USERNAME']
    missingEnvVariable = False

    for variable in env_variables:
        variableValue = os.environ.get(variable)
        if (variableValue == None):
            print("Missing env variable: " + variable)
            missingEnvVariable = True

    return not missingEnvVariable
