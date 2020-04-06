import os
import pymongo
import pandas as pd


USER_MONGODB = os.environ.get('USER_MONGODB')
SECRET_KEY_MONGODB = os.environ.get('SECRET_KEY_MONGODB')
MONGO_URI = 'mongodb+srv://{}:{}@cluster0-bsvmm.mongodb.net/test'.format(USER_MONGODB, SECRET_KEY_MONGODB)
MONGO_DB = 'homes_desc'

class Write:
    def __init__(self, collection_name):

        self.mongo_uri = MONGO_URI
        self.mongo_db = MONGO_DB
        self.collection_name = collection_name
        self.client = pymongo.MongoClient(self.mongo_uri)
        self.db = self.client[self.mongo_db]
        self.collection = self.db[self.collection_name]

    def write_df(self, df):
        self.collection.insert_many(df.to_dict('records'))


if __name__ == '__main__':
    coll_name = 'test'
    d = {'col1': [1, 2], 'col2': [3, 4]}
    df_test = pd.DataFrame(data=d)
    Write(coll_name).write_df(df_test)
