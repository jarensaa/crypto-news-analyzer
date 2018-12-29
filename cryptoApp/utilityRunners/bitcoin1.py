from cryptoApp.socialMediaScraper.scraper import runScraper
from cryptoApp.constants.cryptoRegistry import BITCOIN
from cryptoApp.constants.cryptoRegistry import cryptocurrencies
from cryptoApp.mongoService.setup import getMongoClient
from cryptoApp.mongoService.queries import queryDatabase
from time import mktime
from datetime import datetime
from pprint import pprint
import pymongo
import sys

# YYYY MM DD HH MM SS
startTime = int(mktime(datetime(2017, 10, 1, 12, 00, 00).timetuple()))
endTime = int(mktime(datetime(2017, 10, 1, 23, 59, 59).timetuple()))
currency = BITCOIN
tag = cryptocurrencies[currency]["tag"]


if("--scrape" in sys.argv):
    runScraper(currency, startTime, endTime, 200, 2)

client = getMongoClient()
collection = client.reddit_data.submissions

query = {
    "timestamp": {
        "$gte": startTime,
        "$lte": endTime
    },
    "subreddit": "Bitcoin"
}

results = queryDatabase(collection, query)

# Sort on score:
results = sorted(results, key=lambda k: k["score"], reverse=True)
for i in range(5):
    pprint(results[i])

client.close()
