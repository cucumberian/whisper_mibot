import pymongo

from config import Config
from datetime import datetime


class MongoDB:
    Mongo_string = Config.MongoDB_string or None
    Mongo_dbName = Config.MongoDB_db_name or None

    def __init__(
        self,
        db_string: str = Mongo_string,
        db_name: str = Mongo_dbName,
    ) -> None:
        self.client = pymongo.MongoClient(db_string)
        self.db = self.client[db_name]

    def add_event_to_db(self, event_hash: str, event_date: datetime):
        collection = self.db["events"]
        inserted_data = {"event_hash": event_hash, "time": event_date}
        collection.insert_one(inserted_data)

    def __del__(self):
        self.close()

    def close(self):
        self.client.close()

    # make context manager func
    def __enter__(self):
        return self

    def __exit__(self, exc_type, exc_value, traceback):
        self.close()
