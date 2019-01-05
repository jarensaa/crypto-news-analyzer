from cryptoApp.mongoService.setup import validateMongoEnvironment, getMongoClient
from cryptoApp.constants.unixTime import DAY
from time import mktime
from datetime import datetime


def deleteInRange(collection, startTime, endTime):
    query = {
        "timestamp": {
            "$gte": startTime,
            "$lte": endTime
        }
    }

    return collection.delete_many(query)


# YYYY MM DD HH MM SS
days = 10
startTime = int(mktime(datetime(2017, 12, 11, 00, 00, 00).timetuple()))
endTime = startTime + days * DAY

validateMongoEnvironment()
client = getMongoClient()

print("deleted: ", deleteInRange(client.reddit_data.comments, startTime, endTime).deleted_count)
print("deleted: ", deleteInRange(client.reddit_data.submissions, startTime, endTime).deleted_count)

client.close()
