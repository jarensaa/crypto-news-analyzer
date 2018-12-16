from cryptoApp.socialMediaScraper.scraper import runScraper
from cryptoApp.socialMediaAggregator.aggregator import runAggregator
from cryptoApp.timelinePlotter.storageService import buildSocialMediaSeries
from cryptoApp.timelinePlotter.storageService import buildCryptoDataSeries
from cryptoApp.constants.cryptoRegistry import BITCOIN
from cryptoApp.constants.cryptoRegistry import cryptocurrencies
from cryptoApp.constants.unixTime import DAY
from cryptoApp.constants.unixTime import HOUR
from cryptoApp.timelinePlotter.plotter import plot
from time import mktime
from datetime import datetime
import sys

# YYYY MM DD HH MM SS
days = 10
startTime = int(mktime(datetime(2018, 11, 1, 0, 00, 00).timetuple()))
endTime = startTime + days * DAY
granularity = HOUR
currency = BITCOIN
tag = cryptocurrencies[currency]["tag"]

# Scrape data from reddit
for dayIndex in range(days):
    intervalStart = startTime + dayIndex * DAY
    intervalEnd = startTime + DAY + dayIndex * DAY
    runScraper(currency, intervalStart, intervalEnd, 200, 2)

seriesId = runAggregator(startTime, endTime, tag, submissionScoreWeight=1,
                         submissionWeight=10, commentWeight=5, commentScoreWeight=0.5)
buildSocialMediaSeries(seriesId)

if("--plot" in sys.argv):
    buildCryptoDataSeries(startTime, endTime, currency)
    plot()