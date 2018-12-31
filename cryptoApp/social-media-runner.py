from cryptoApp.socialMediaScraper.scraper import runScraper
from cryptoApp.socialMediaAggregator.aggregator import runAggregator
from cryptoApp.timelinePlotter.storageService import buildSocialMediaSeries
from cryptoApp.timelinePlotter.storageService import buildCryptoDataSeries
from cryptoApp.socialMediaEventDetection.detector import runEventDetector
from cryptoApp.constants.cryptoRegistry import BITCOIN
from cryptoApp.constants.cryptoRegistry import cryptocurrencies
from cryptoApp.constants.unixTime import DAY
from cryptoApp.constants.unixTime import HOUR
from cryptoApp.timelinePlotter.plotter import plot
from time import mktime
from datetime import datetime
import sys

# YYYY MM DD HH MM SS
days = 200
startTime = int(mktime(datetime(2017, 11, 10, 0, 00, 00).timetuple()))
endTime = startTime + days * DAY
granularity = HOUR
currency = BITCOIN
tag = cryptocurrencies[currency]["tag"]

peakDetectionWindowSize = 10
peakDetectionSensitivity = 2

# Scrape data from reddit

if("--noscrape" not in sys.argv):
    for dayIndex in range(days):
        intervalStart = startTime + dayIndex * DAY
        intervalEnd = startTime + DAY + dayIndex * DAY
        runScraper(currency, intervalStart, intervalEnd, 600, 2)
        print("{}:{} scraped".format(datetime.fromtimestamp(startTime).strftime(
            '%Y-%m-%d'), datetime.fromtimestamp(intervalEnd).strftime('%Y-%m-%d')))

seriesId = runAggregator(startTime, endTime, tag, submissionScoreWeight=1,
                         submissionWeight=10, commentWeight=5, commentScoreWeight=0.5)

runEventDetector(seriesId, peakDetectionWindowSize, peakDetectionSensitivity)
buildSocialMediaSeries(seriesId)

if("--plot" in sys.argv):
    buildCryptoDataSeries(startTime, endTime, currency)
    plot()
