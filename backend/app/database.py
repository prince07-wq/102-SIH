import os
from functools import lru_cache

from pymongo import MongoClient
from dotenv import load_dotenv

load_dotenv()


@lru_cache(maxsize=1)
def get_mongo_client():
    """Creates the Mongo client only when an authentication request needs it."""
    mongo_uri = os.getenv("MONGO_URI")
    if not mongo_uri:
        raise RuntimeError("MONGO_URI is not set")
    return MongoClient(mongo_uri, serverSelectionTimeoutMS=5000)


def get_users_collection():
    return get_mongo_client()["mplads"]["users"]
