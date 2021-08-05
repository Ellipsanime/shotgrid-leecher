import os

import shotgun_api3 as sg
from motor.motor_asyncio import AsyncIOMotorClient
from pymongo import MongoClient
from toolz import memoize


@memoize
def get_db_client() -> MongoClient:
    return MongoClient(os.getenv("MONGODB_URL"))


@memoize
def get_async_db_client() -> AsyncIOMotorClient:
    return AsyncIOMotorClient(os.getenv("MONGODB_URL"))


@memoize
def get_shotgrid_client() -> sg.Shotgun:
    url = os.getenv("SHOTGRID_URL")
    login = os.getenv("SHOTGRID_LOGIN")
    password = os.getenv("SHOTGRID_PASSWORD")
    return sg.Shotgun(url, login=login, password=password)
