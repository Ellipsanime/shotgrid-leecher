import os

import shotgun_api3 as sg
from toolz import memoize
from pymongo import MongoClient


@memoize
def get_db_client() -> MongoClient:
    return MongoClient(os.getenv("MONGODB_URL"))


@memoize
def get_shotgrid_client() -> sg.Shotgun:
    url = os.getenv("SHOTGRID_URL")
    login = os.getenv("SHOTGRID_LOGIN")
    password = os.getenv("SHOTGRID_PASSWORD")
    return sg.Shotgun(url, login=login, password=password)
