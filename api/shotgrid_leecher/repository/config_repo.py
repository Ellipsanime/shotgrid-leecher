from typing import List, Callable

from pymongo.collection import Collection

from shotgrid_leecher.record.enums import DbName, DbCollection
from shotgrid_leecher.record.leecher_structures import ShotgridCredentials
from shotgrid_leecher.utils.connectivity import db_collection
from shotgrid_leecher.utils.logger import get_logger

_LOG = get_logger(__name__.split(".")[-1])

_collection: Callable[[DbCollection], Collection] = db_collection(
    DbName.LEECHER
)


def fetch_credentials() -> List[ShotgridCredentials]:
    return [
        ShotgridCredentials.from_mongo(x)
        for x in _collection(DbCollection.SHOTGRID_CREDENTIALS).find({})
    ]


def fetch_shotgrid_urls() -> List[str]:
    return [x.shotgrid_url for x in fetch_credentials()]
