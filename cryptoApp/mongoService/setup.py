import pymongo
import os

MONGOPW = os.environ.get('MONGOPW')
MONGOUSER = os.environ.get('MONGOUSER')


def validateMongoEnvironment():
    """ Validates if mongoDB environment variables are set.
      Returns:
      boolean -- True if environment is valid, False if not.
    """
    valid = True

    if(MONGOPW == None):
        print("MONGOPW environment variable is missing")
        valid = False
    if(MONGOUSER == None):
        print("MONGOUSER environment variable is missing")
        valid = False
    return valid


def getMongoClient():
    """Uses environemt variables to connect to the Mongo DB instance.
      Returns:
        pymongo.mongo_client -- A pymongo client which can be used to interact with the database.
    """
    connectionString = "mongodb://{}:{}@cluster-kaw-shard-00-00-loi4k.mongodb.net:27017,cluster-kaw-shard-00-01-loi4k.mongodb.net:27017,cluster-kaw-shard-00-02-loi4k.mongodb.net:27017/test?ssl=true&replicaSet=cluster-kaw-shard-0&authSource=admin&retryWrites=true".format(
        MONGOUSER, MONGOPW
    )
    try:
        client = pymongo.MongoClient(connectionString)
        print("Connected successfully to MongoDB.")
    except:
        print("Could not connect to MongoDB")
        exit()
    return client
