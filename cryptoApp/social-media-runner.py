from cryptoApp.socialMediaScraper.scraper import runScraper
from cryptoApp.socialMediaAggregator.aggregator import runAggregator
#from cryptoApp.timelinePlotter.storageService import buildSeries
from cryptoApp.constants.cryptoRegistry import BITCOIN
from cryptoApp.constants.cryptoRegistry import cryptocurrencies
from cryptoApp.constants.unixTime import DAY
from cryptoApp.constants.unixTime import HOUR

from time import mktime
from datetime import datetime

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

seriesId = runAggregator(startTime, endTime, currency)
# buildSeries(seriesId)
