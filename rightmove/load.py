import pymongo
import pandas as pd
import os
import sys

USER_MONGODB = os.environ.get('USER_MONGODB')
SECRET_KEY_MONGODB = os.environ.get('SECRET_KEY_MONGODB')
MONGO_URI = 'mongodb+srv://{}:{}@cluster0-bsvmm.mongodb.net/test'.format(USER_MONGODB, SECRET_KEY_MONGODB)
MONGO_DB = 'homes_desc'



class Load:
    def __init__(self, collection_name):
        self.mongo_uri = MONGO_URI
        self.mongo_db = MONGO_DB
        self.collection_name = collection_name
        self.client = pymongo.MongoClient(self.mongo_uri)
        self.db = self.client[self.mongo_db]
        self.collection = self.db[self.collection_name]
        self.df = pd.DataFrame()

    def read_db(self, query={}, no_id=True):
        # Make a query to the specific DB and Collection
        cursor = self.collection.find(query)

        # Expand the cursor and construct the DataFrame
        self.df = pd.DataFrame(list(cursor))

        # Delete the _id
        if no_id:
            del self.df['_id']

        return self.df

    def select_distinct(self, col='area'):
        # Make a query to the specific DB and Collection
        unique_col = self.collection.distinct(col)

        return unique_col


if __name__ == '__main__':
    coll_name = 'rightmove'
    df_rightmove = Load(coll_name).read_db()
    print(df_rightmove.head())

    unique_area = Load(coll_name).select_distinct()
    print(unique_area)


