from typing import Callable

from pymongo import UpdateOne
from pymongo.collection import Collection
from pymongo.results import BulkWriteResult

from shotgrid_leecher.record.commands import UpsertProjectUserLinksCommand
from shotgrid_leecher.record.enums import DbName, DbCollection
from shotgrid_leecher.utils.connectivity import db_collection
from shotgrid_leecher.utils.logger import get_logger

_LOG = get_logger(__name__.split(".")[-1])

_collection: Callable[[DbCollection], Collection] = db_collection(
    DbName.LEECHER
)


def delete_links_by_host_url(host_url: str) -> None:
    _collection(DbCollection.SHOTGRID_PROJ_USER_LINKS).delete_many(
        {"host_url": host_url},
    )


def upsert_project_user_links(
    command: UpsertProjectUserLinksCommand,
) -> BulkWriteResult:
    links_table = _collection(DbCollection.SHOTGRID_PROJ_USER_LINKS)
    documents = [
        UpdateOne(
            {"_id": x.id},
            {"$set": x.to_base_dict()},
            upsert=True,
        )
        for x in command.links
    ]
    return links_table.bulk_write(documents)
