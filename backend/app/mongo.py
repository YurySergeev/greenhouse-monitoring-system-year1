import os
from pymongo import MongoClient
from dotenv import load_dotenv
from pprint import pprint

load_dotenv()

class TEST_DB_CONNECTION():
    def __init__(self):
        self.mongo_uri = os.getenv("MONGO_URI")
        self.db_name = os.getenv("DB_NAME")

        print("URI_LOADED: ", bool(self.mongo_uri))
        print("DB_NAME: ", self.db_name)

        if not self.mongo_uri or not self.db_name:
            raise RuntimeError("MONGO_URI and DB_NAME are not set")

        self.client = MongoClient(self.mongo_uri, serverSelectionTimeoutMS=5000)
        # Force an actual connection check:
        self.client.admin.command("ping")
        self.db = self.client[self.db_name]


        print("Connection runs successfully")
        print("Database created", self.client.list_database_names())


if __name__ == "__main__":
    db = TEST_DB_CONNECTION()