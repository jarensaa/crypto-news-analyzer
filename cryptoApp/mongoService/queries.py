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

    collection.insert_many(objects)
    print("Posted {:d} new objects to MongoDB".format(len(objects)))
