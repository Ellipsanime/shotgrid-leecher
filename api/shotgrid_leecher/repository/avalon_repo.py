from toolz import pipe

import utils.connectivity as conn
from record.avalon_structures import AvalonProject
from record.enums import DbName, ShotgridType


def _get_avalon_database():
    return conn.get_db_client().get_database(DbName.AVALON.value)


def fetch_project(project_name: str) -> AvalonProject:
    return pipe(
        _get_avalon_database().get_collection(project_name),
        lambda x: x.find_one({"type": ShotgridType.PROJECT.value.lower()}),
        AvalonProject.from_dict,
    )
