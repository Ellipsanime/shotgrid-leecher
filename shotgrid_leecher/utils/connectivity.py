import os
import threading
from typing import List, Any, Dict

import shotgun_api3 as sg
from motor.motor_asyncio import AsyncIOMotorClient
from pymongo import MongoClient
from pymongo.collection import Collection
from retry import retry
from toolz import memoize

from shotgrid_leecher.record.enums import EventTables
from shotgrid_leecher.record.shotgrid_structures import ShotgridCredentials

Map = Dict[str, Any]


class ShotgridClient:
    client: sg.Shotgun

    def __init__(self, client: sg.Shotgun) -> None:
        self.client = client

    @retry(tries=3, backoff=0.7)
    def find_one(
        self, type_: str, filters: List[List[Any]], fields: List[str]
    ) -> Map:
        return self.client.find_one(type_, filters, fields)

    @retry(tries=3, backoff=1.5)
    def find(
        self, type_: str, filters: List[List[Any]], fields: List[str]
    ) -> List[Map]:
        return self.client.find(type_, filters, fields)


@memoize
def get_db_client(connection_id=threading.get_ident()) -> MongoClient:
    # TODO log properly
    print(f"Mongo connection initialized for id {connection_id}")
    return MongoClient(os.getenv("MONGODB_URL"))


def get_collection(table: EventTables) -> Collection:
    return get_db_client().openpype_shotgrid[table.value]


@memoize
def get_async_db_client() -> AsyncIOMotorClient:
    return AsyncIOMotorClient(os.getenv("MONGODB_URL"))


@memoize
def get_shotgrid_client(credentials: ShotgridCredentials) -> ShotgridClient:
    url = credentials.shotgrid_url
    script_name = credentials.script_name
    api_key = credentials.script_key
    sg_client = sg.Shotgun(url, script_name=script_name, api_key=api_key)
    return ShotgridClient(sg_client)
