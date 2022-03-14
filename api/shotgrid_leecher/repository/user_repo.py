from typing import Callable, List

from pymongo.collection import Collection

from shotgrid_leecher.record.enums import DbName, DbCollection
from shotgrid_leecher.record.queries import ShotgridFetchUserProjectLinksQuery
from shotgrid_leecher.record.shotgrid_structures import ShotgridProjectUserLink
from shotgrid_leecher.utils.connectivity import db_collection
from shotgrid_leecher.utils.logger import get_logger

_LOG = get_logger(__name__.split(".")[-1])

_collection: Callable[[DbCollection], Collection] = db_collection(
    DbName.LEECHER
)


def fetch_project_user_links(
    query: ShotgridFetchUserProjectLinksQuery,
) -> List[ShotgridProjectUserLink]:
    links_table = _collection(DbCollection.SHOTGRID_PROJ_USER_LINKS)
    return [
        ShotgridProjectUserLink.from_dict(x)
        for x in links_table.find({"user_email": query.email})
    ]
