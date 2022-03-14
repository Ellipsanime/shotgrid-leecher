from email.utils import parseaddr
from typing import List, Dict, Any

from cachetools import cached, TTLCache
from toolz import pipe, curry
from toolz.curried import (
    map as select,
    filter as where,
)

import shotgrid_leecher.mapper.entity_mapper as mapper
import shotgrid_leecher.utils.connectivity as conn
from shotgrid_leecher.record.enums import ShotgridType
from shotgrid_leecher.record.queries import ShotgridFindUserProjectLinkQuery
from shotgrid_leecher.record.shotgrid_filters import (
    TypeIsFilter,
    IsNotFilter,
    CompositeFilter,
)
from shotgrid_leecher.record.shotgrid_structures import ShotgridProjectUserLink

_EMAIL = "email"
Map = Dict[str, Any]
_F = CompositeFilter
_TYPE = TypeIsFilter
_NOT = IsNotFilter


def _fetch_all_users(
    query: ShotgridFindUserProjectLinkQuery,
) -> Dict[int, Map]:
    client = conn.get_shotgrid_client(query.credentials)
    return pipe(
        client.find(
            ShotgridType.HUMAN_USER.value,
            _F.filter_by(_NOT(_EMAIL, None)),
            list(query.user_fields),
        ),
        where(lambda x: parseaddr(x.get(_EMAIL))[-1]),
        select(lambda x: (x["id"], x)),
        dict,
    )


@curry
def _fetch_all_user_project_links(
    query: ShotgridFindUserProjectLinkQuery,
    users: Dict[int, Map],
) -> Dict[int, Map]:
    client = conn.get_shotgrid_client(query.credentials)
    return pipe(
        client.find(
            ShotgridType.PROJECT_USER_LINK.value,
            _F.filter_by(_TYPE("user", ShotgridType.HUMAN_USER)),
            list(query.linkage_fields),
        ),
        where(lambda x: users.get(x.get("user", dict()).get("id"))),
        select(
            lambda x: mapper.to_shotgrid_project_user_link(
                query.credentials.shotgrid_url, users[x["user"]["id"]], x
            )
        ),
    )


@cached(cache=TTLCache(maxsize=24, ttl=60), key=lambda x: x.credentials)
def find_linked_projects(
    query: ShotgridFindUserProjectLinkQuery,
) -> List[ShotgridProjectUserLink]:
    return pipe(
        _fetch_all_users(query),
        _fetch_all_user_project_links(query),
        list,
    )
