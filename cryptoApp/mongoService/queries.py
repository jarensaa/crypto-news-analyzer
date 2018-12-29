import sys
from pymongo import InsertOne
from pymongo.errors import BulkWriteError


def queryDatabase(collection, jsonQuery):
    """Queries mongodb collection.

    Arguments:
      collection {pymongo.database.collection} -- The collection to query
      jsonQuery {dict()} -- A json object in the form a dict, correponding to the mongoDB query.

    Returns:
      list() -- The results from the query
    """

    results = []
    for result in collection.find(jsonQuery):
        results.append(result)
    return results


def bulkPostToDatabase(collection, objects):
    """ Post a list of objects to the mongoDB database with the bulk api.

    Arguments:
      collection {pymongo.database.collection} -- The database collection to post to.
      objects {list()} -- A list of json objects (dict) to post.
    """
    if(len(objects) == 0):
        return

    collection.insert_many(objects)
    print("Posted {:d} new objects to MongoDB".format(len(objects)))


def bulkPostUniqueToDatabase(collection, objects):
    """ Post a list of objects to the mongoDB database with the bulk api. Use for objects with custom _id field.
    Ensures that duplicates are ignored, while new data is posted.

    Arguments:
      collection {[type]} -- [description]
      objects {[type]} -- [description]
    """
    if(len(objects) == 0):
        return

    requests = []
    for Object in objects:
        requests.append(InsertOne(Object))

    try:
        response = collection.bulk_write(requests, ordered=False)
        return (len(requests))
    except BulkWriteError as error:
        return error.details['nInserted']


def postSingleObjectToDatabase(collection, input_object):
    collection.insert_one(input_object)
