import uuid
from typing import Dict, Any, List

import pytest
from _pytest.monkeypatch import MonkeyPatch
from assertpy import assert_that
from mongomock.mongo_client import MongoClient

import shotgrid_leecher.repository.shotgrid_user_repo as shotgrid_repo
from shotgrid_leecher.domain import user_domain
from shotgrid_leecher.record.enums import DbName, DbCollection
from shotgrid_leecher.record.leecher_structures import ShotgridCredentials
from shotgrid_leecher.record.shotgrid_structures import ShotgridProjectUserLink
from shotgrid_leecher.utils import connectivity as conn
from utils.funcs import (
    fun,
)

Map = Dict[str, Any]


def _all_links(client: MongoClient) -> List[Map]:
    return list(
        client.get_database(DbName.LEECHER.value)
        .get_collection(DbCollection.SHOTGRID_PROJ_USER_LINKS.value)
        .find({})
    )


def _insert_credentials(client: MongoClient, dic: Map) -> Any:
    return client.get_database(DbName.LEECHER.value).get_collection(
        DbCollection.SHOTGRID_CREDENTIALS.value
    ).insert_one(dic)


def _fetch_linked_projects(size=10) -> List[ShotgridProjectUserLink]:
    return [
        ShotgridProjectUserLink(
            id=str(x+1),
            host_url=f"http://{str(uuid.uuid4())[:5]}.com",
            type=str(uuid.uuid4())[:5],
            user_email=str(uuid.uuid4())[:5],
            user_name=str(uuid.uuid4())[:5],
            user_id=x+1,
            project_id=x+1,
            project_name=str(uuid.uuid4())[:5],
        )
        for x in range(size)
    ]


@pytest.mark.asyncio
async def test_insert_project_user_links(monkeypatch: MonkeyPatch):
    # Arrange
    client = MongoClient()
    url = f"http://{str(uuid.uuid4())[:5]}.com"
    _insert_credentials(client, ShotgridCredentials(url, "", "").to_mongo())
    monkeypatch.setattr(conn, "get_db_client", fun(client))
    monkeypatch.setattr(shotgrid_repo, "find_linked_projects", fun(_fetch_linked_projects(10)))
    # Act
    await user_domain.synchronize_project_user_links()

    # Assert
    assert_that(_all_links(client)).extracting("_id").is_equal_to(
        list(map(str, range(1, 10+1)))
    )
    assert_that(_all_links(client)).extracting("user_id").is_equal_to(
        list(range(1, 10+1))
    )
    assert_that(_all_links(client)).extracting("project_id").is_equal_to(
        list(range(1, 10+1))
    )
